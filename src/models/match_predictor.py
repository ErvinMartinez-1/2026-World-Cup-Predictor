import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional
import joblib
import warnings
warnings.filterwarnings('ignore')

from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression, PoissonRegressor
from sklearn.metrics import accuracy_score, f1_score, log_loss, mean_absolute_error, mean_squared_error
from sklearn.model_selection import cross_val_score

from src.config import DATA_PROCESSED


class MatchPredictor:
    """
    Trains two models:
      1. XGBoost Classifier  → predicts match result (home_win/draw/away_win)
      2. Poisson Regressor   → predicts goals scored by each team

    Both are validated on a time-based split to prevent data leakage.

    Usage:
        predictor = MatchPredictor()
        predictor.train(X_train, y_train, X_val, y_val)
        predictor.evaluate(X_test, y_test)
        predictor.save("data/processed/models/")
    """
    RESULT_ENCODING = {0: 'home_win', 1: 'draw', 2: 'away_win'}
    RESULT_DECODING = {'home_win': 0, 'draw': 1, 'away_win': 2}

    def __init__(self):
        self.classifier = XGBClassifier(
            n_estimators=300,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.7,
            colsample_bytree=0.6,
            min_child_weight=5,
            reg_alpha=0.1, # L1 regularisation (feature sparsity)
            reg_lamda=1.5, # L2 regularisation (weight penalty)
            gamma=0.1,
            early_stopping_rounds=30,
            objective='multi:softprob', # outputs probabilities not labels
            num_class=3,
            eval_metric='mlogloss',
            use_label_encoder=False,
            random_state=42,
            n_jobs=-1 # use all CPU cores
        )

        # If XGBoost doesn't beat logistic regression, something is wrong with the features.
        self.baseline_classifier = LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight='balanced' #handles home_win imbalance
        )

        self.home_goal_regressor = PoissonRegressor(
            alpha=0.1,
            max_iter=1000
        )
        self.away_goal_regressor = PoissonRegressor(
            alpha=0.1,
            max_iter=1000
        )

        self.is_trained_ = False
        self.feature_names_  = None
        self.train_metrics_  = {}
        self.val_metrics_ = {}

    # TRAINING
    def train(self, X_train: pd.DataFrame, y_train: pd.DataFrame, X_val:   pd.DataFrame, y_val:   pd.DataFrame) -> "MatchPredictor":
        # Train all models and evaluate on the validation set.
        self.feature_names_ = list(X_train.columns)

        print("═" * 55)
        print("  Phase 3: Model Training")
        print("═" * 55)
        print(f"  Train samples: {len(X_train):,}")
        print(f"  Val samples:   {len(X_val):,}")
        print(f"  Features:      {len(self.feature_names_)}\n")

        self.train_baseline(X_train, y_train, X_val, y_val)

        self.train_classifier(X_train, y_train, X_val, y_val)

        self.train_regressors(X_train, y_train, X_val, y_val)

        self.print_feature_importance(top_n=15)

        self.is_trained_ = True
        return self

    def train_baseline(self, X_train, y_train, X_val, y_val):
        print("── Baseline: Logistic Regression ────────────────────")
        y_tr = y_train['result_encoded']
        y_vl = y_val['result_encoded']

        self.baseline_classifier.fit(X_train, y_tr)

        train_acc = accuracy_score(y_tr, self.baseline_classifier.predict(X_train))
        val_acc = accuracy_score(y_vl, self.baseline_classifier.predict(X_val))
        val_f1 = f1_score(y_vl, self.baseline_classifier.predict(X_val), average='weighted')

        print(f"  Train accuracy: {train_acc:.4f}")
        print(f"  Val accuracy:   {val_acc:.4f}")
        print(f"  Val F1:         {val_f1:.4f}\n")

        self.train_metrics_['baseline_accuracy'] = train_acc
        self.val_metrics_['baseline_accuracy'] = val_acc
        self.val_metrics_['baseline_f1'] = val_f1

    def train_classifier(self, X_train, y_train, X_val, y_val):
        # Train XGBoost classifier with early stopping.
        # Early stopping: stops training when validation loss stops improving for 50 consecutive rounds. Prevents overfitting automatically andsaves training time.
        print("── XGBoost Classifier ───────────────────────────────")
        y_tr = y_train['result_encoded']
        y_vl = y_val['result_encoded']

        # Compute class weights to handle home_win imbalance
        # balanced: weight = total_samples / (n_classes * class_count)
        class_counts  = y_tr.value_counts().sort_index()
        total = len(y_tr)
        n_classes = 3
        class_weights = {i: total / (n_classes * count) for i, count in class_counts.items()}
        tournament_weights = y_train['weight'] if 'weight' in y_train.columns else pd.Series(1.0, index=y_train.index)
        sample_weights = y_tr.map(class_weights) * tournament_weights.values

        print(f"  Class weights: { {self.RESULT_ENCODING[k]: round(v,3) for k,v in class_weights.items()} }")

        # Train with early stopping on validation set
        self.classifier.fit(
            X_train, y_tr,
            sample_weight=sample_weights,
            eval_set=[(X_val, y_vl)],
            verbose=False,
        )

        #Training metrics
        train_pred = self.classifier.predict(X_train)
        train_probs = self.classifier.predict_proba(X_train)
        train_acc = accuracy_score(y_tr, train_pred)
        train_loss = log_loss(y_tr, train_probs)

        #Validation metrics
        val_pred = self.classifier.predict(X_val)
        val_probs = self.classifier.predict_proba(X_val)
        val_acc = accuracy_score(y_vl, val_pred)
        val_f1 = f1_score(y_vl, val_pred, average='weighted')
        val_loss = log_loss(y_vl, val_probs)
        val_rps = self.ranked_probability_score(y_vl, val_probs)

        f1_per_class = f1_score(y_vl, val_pred, average=None)

        print(f"\n  Train accuracy:   {train_acc:.4f}")
        print(f"  Train log loss:   {train_loss:.4f}")
        print(f"\n  Val accuracy:     {val_acc:.4f}  "
              f"({'↑' if val_acc > self.val_metrics_['baseline_accuracy'] else '↓'} baseline)")
        print(f"  Val F1 weighted:  {val_f1:.4f}")
        print(f"  Val log loss:     {val_loss:.4f}")
        print(f"  Val RPS:          {val_rps:.4f}  (lower is better)")
        print(f"\n  Per-class F1:")
        for i, f1 in enumerate(f1_per_class):
            print(f"    {self.RESULT_ENCODING[i]:<12}: {f1:.4f}")

        self.train_metrics_.update({
            'xgb_accuracy': train_acc,
            'xgb_log_loss': train_loss,
        })
        self.val_metrics_.update({
            'xgb_accuracy': val_acc,
            'xgb_f1':       val_f1,
            'xgb_log_loss': val_loss,
            'xgb_rps':      val_rps,
        })

    def train_regressors(self, X_train, y_train, X_val, y_val):
        print("\n── Poisson Goal Regressors ──────────────────────────")

        for target, model, label in [('home_score', self.home_goal_regressor, 'Home goals'), ('away_score', self.away_goal_regressor, 'Away goals')]:
            # Filter to completed matches only
            train_mask = y_train[target].notna()
            val_mask   = y_val[target].notna()

            y_tr = y_train.loc[train_mask, target].clip(lower=0)
            y_vl = y_val.loc[val_mask, target].clip(lower=0)
            X_tr = X_train[train_mask]
            X_vl = X_val[val_mask]

            model.fit(X_tr, y_tr)

            val_pred = model.predict(X_vl)
            val_mae  = mean_absolute_error(y_vl, val_pred)
            val_rmse = np.sqrt(mean_squared_error(y_vl, val_pred))

            print(f"\n  {label} ({len(y_tr):,} train / {len(y_vl):,} val matches):")
            print(f"    Val MAE:       {val_mae:.4f} goals")
            print(f"    Val RMSE:      {val_rmse:.4f} goals")
            print(f"    Avg predicted: {val_pred.mean():.4f}")
            print(f"    Avg actual:    {y_vl.mean():.4f}")

            self.val_metrics_[f'{target}_mae']  = val_mae
            self.val_metrics_[f'{target}_rmse'] = val_rmse

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Generate predictions for a set of fixtures.

        Returns DataFrame with:
          - prob_home_win, prob_draw, prob_away_win
          - predicted_result
          - predicted_home_goals, predicted_away_goals
          - predicted_score (e.g. "2-1")
        """
        self.require_trained()
        X = self.align_features(X)

        # ── Classification probabilities ──
        probs = self.classifier.predict_proba(X)
        pred_class  = self.classifier.predict(X)

        # ── Goal predictions ──
        home_goals = self.home_goal_regressor.predict(X)
        away_goals = self.away_goal_regressor.predict(X)

        return pd.DataFrame({
            'prob_home_win': probs[:, 0].round(4),
            'prob_draw': probs[:, 1].round(4),
            'prob_away_win': probs[:, 2].round(4),
            'predicted_result':[self.RESULT_ENCODING[p] for p in pred_class],
            'predicted_home_goals': np.round(home_goals, 2),
            'predicted_away_goals': np.round(away_goals, 2),
            'predicted_score': [f"{round(h)}-{round(a)}" for h, a in zip(home_goals, away_goals)]
        }, index=X.index)

    def predict_single(self, features: dict) -> dict:
        X = pd.DataFrame([features])
        return self.predict(X).iloc[0].to_dict()

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.DataFrame, label:  str = "Test") -> dict:
        self.require_trained()
        X_test = self.align_features(X_test)

        pred_class  = self.classifier.predict(X_test)
        pred_probs  = self.classifier.predict_proba(X_test)
        y_true = y_test['result_encoded']

        acc = accuracy_score(y_true, pred_class)
        f1 = f1_score(y_true, pred_class, average='weighted')
        ll = log_loss(y_true, pred_probs)
        rps = self.ranked_probability_score(y_true, pred_probs)
        f1_cls  = f1_score(y_true, pred_class, average=None)

        print(f"\n── {label} Set Evaluation ─────────────────────────")
        print(f"  Accuracy:        {acc:.4f}")
        print(f"  F1 weighted:     {f1:.4f}")
        print(f"  Log Loss:        {ll:.4f}")
        print(f"  RPS:             {rps:.4f}  (lower is better)")
        print(f"\n  Per-class F1:")
        for i, score in enumerate(f1_cls):
            print(f"    {self.RESULT_ENCODING[i]:<12}: {score:.4f}")

        # Goal evaluation, only on completed matches 
        for target, model in [('home_score', self.home_goal_regressor), ('away_score', self.away_goal_regressor)]:
            if target not in y_test.columns:
                continue

            # Filter to rows where the score is known (match already played)
            valid_mask = y_test[target].notna()
            valid_count = valid_mask.sum()

            if valid_count == 0:
                print(f"\n  {target}: no completed matches in test set")
                continue

            X_valid = X_test[valid_mask]
            y_valid = y_test.loc[valid_mask, target]
            preds = model.predict(X_valid)

            mae = mean_absolute_error(y_valid, preds)
            rmse = np.sqrt(mean_squared_error(y_valid, preds))

            print(f"\n  {target} ({valid_count} matches):")
            print(f"    MAE:  {mae:.4f} goals")
            print(f"    RMSE: {rmse:.4f} goals")

        return {
            'accuracy': acc, 'f1': f1,
            'log_loss': ll,  'rps': rps,
        }

    def save(self, directory: Path):
        # Save all models and metadata to directory.
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        joblib.dump(self.classifier, directory / "classifier.joblib")
        joblib.dump(self.baseline_classifier, directory / "baseline.joblib")
        joblib.dump(self.home_goal_regressor, directory / "home_goals.joblib")
        joblib.dump(self.away_goal_regressor, directory / "away_goals.joblib")
        joblib.dump(self.feature_names_, directory / "feature_names.joblib")

        metrics = {
            'train': self.train_metrics_,
            'val': self.val_metrics_,
        }
        joblib.dump(metrics, directory / "metrics.joblib")
        print(f"\n[MatchPredictor] ✅ All models saved → {directory}")

    @classmethod
    def load(cls, directory: Path) -> "MatchPredictor":
        # Load a trained MatchPredictor from disk
        directory = Path(directory)
        predictor = cls()

        predictor.classifier = joblib.load(directory / "classifier.joblib")
        predictor.baseline_classifier = joblib.load(directory / "baseline.joblib")
        predictor.home_goal_regressor = joblib.load(directory / "home_goals.joblib")
        predictor.away_goal_regressor = joblib.load(directory / "away_goals.joblib")
        predictor.feature_names_ = joblib.load(directory / "feature_names.joblib")

        metrics = joblib.load(directory / "metrics.joblib")
        predictor.train_metrics_ = metrics['train']
        predictor.val_metrics_ = metrics['val']
        predictor.is_trained_  = True

        print(f"[MatchPredictor] Loaded from {directory}")
        return predictor

    def ranked_probability_score(self, y_true:  pd.Series, y_probs: np.ndarray) -> float:
        # Ranked Probability Score (RPS) — the gold standard metric for football prediction models.
        n = len(y_true)
        rps_sum = 0.0

        # Ordered categories: home_win=0, draw=1, away_win=2
        for i, (true_class, probs) in enumerate(
            zip(y_true, y_probs)
        ):
            # Cumulative probabilities
            cum_probs = np.cumsum(probs)
            # Cumulative actuals (step function)
            cum_true  = np.array([
                1.0 if true_class <= j else 0.0
                for j in range(len(probs))
            ])
            # RPS for this match
            rps_sum += np.sum((cum_probs - cum_true) ** 2) / (len(probs) - 1)

        return rps_sum / n

    def print_feature_importance(self, top_n: int = 15):
        print(f"\n── Top {top_n} Most Important Features ──────────────")
        importance = pd.Series(
            self.classifier.feature_importances_,
            index=self.feature_names_
        ).sort_values(ascending=False)

        for feat, score in importance.head(top_n).items():
            bar   = '█' * int(score * 200)
            print(f"  {feat:<35} {score:.4f}  {bar}")

    def align_features(self, X: pd.DataFrame) -> pd.DataFrame:
        for col in self.feature_names_:
            if col not in X.columns:
                X[col] = 0
        return X[self.feature_names_]

    def require_trained(self):
        if not self.is_trained_:
            raise RuntimeError(
                "Model not trained. Call .train() first."
            )