import { useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { NotchNav } from "./ui/notch-nav";

const NAV_ITEMS = [
  { value: "/", label: "Home" },
  { value: "/predictions", label: "Predictions" },
];

export default function NavBar() {
  const location = useLocation();
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 5);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const isHome = location.pathname === "/";
  const hidden = isHome && !scrolled;

  // Resolve active tab: exact match for "/", prefix match for deeper routes
  const activeValue =
    NAV_ITEMS.find((item) =>
      item.value === "/"
        ? location.pathname === "/"
        : location.pathname.startsWith(item.value)
    )?.value ?? "/";

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200 shadow-sm px-6 py-3 flex items-center justify-center transition-all duration-300 ease-out ${
        hidden ? "-translate-y-full opacity-0" : "translate-y-0 opacity-100"
      }`}
    >
      <NotchNav
        items={NAV_ITEMS}
        value={activeValue}
        onValueChange={(path) => navigate(path)}
        ariaLabel="Site navigation"
      />
    </nav>
  );
}
