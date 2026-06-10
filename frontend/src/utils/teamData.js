export const ISO_MAP = {
  // A
  "Mexico": "mx", "South Korea": "kr", "South Africa": "za", "Czech Republic": "cz",
  // B
  "Canada": "ca", "Switzerland": "ch", "Bosnia and Herzegovina": "ba", "Qatar": "qa",
  // C
  "Brazil": "br", "Morocco": "ma", "Haiti": "ht", "Scotland": "gb-sct",
  // D
  "Paraguay": "py", "United States": "us", "Australia": "au", "Turkey": "tr",
  // E
  "Germany": "de", "Curaçao": "cw", "Ivory Coast": "ci", "Ecuador": "ec",
  // F
  "Netherlands": "nl", "Japan": "jp", "Tunisia": "tn", "Sweden": "se",
  // G
  "Belgium": "be", "Egypt": "eg", "Iran": "ir", "New Zealand": "nz",
  // H
  "Spain": "es", "Cape Verde": "cv", "Saudi Arabia": "sa", "Uruguay": "uy",
  // I
  "France": "fr", "Senegal": "sn", "Norway": "no", "Iraq": "iq",
  // J
  "Argentina": "ar", "Algeria": "dz", "Austria": "at", "Jordan": "jo",
  // K
  "Portugal": "pt", "Uzbekistan": "uz", "Colombia": "co", "DR Congo": "cd",
  // L
  "England": "gb-eng", "Croatia": "hr", "Ghana": "gh", "Panama": "pa",
};

export const SHORT_NAMES = {
  "Bosnia and Herzegovina": "Bosnia & Herz.",
  "United States":          "USA",
  "Czech Republic":         "Czech Rep.",
  "South Korea":            "S. Korea",
  "South Africa":           "S. Africa",
  "Saudi Arabia":           "Saudi Arabia",
  "New Zealand":            "New Zealand",
  "Ivory Coast":            "Ivory Coast",
};

// Primary bg color + readable accent for champion card
export const NATION_COLORS = {
  "Mexico":                 { bg: "#006847", accent: "#FFFFFF" },
  "South Korea":            { bg: "#003478", accent: "#FFFFFF" },
  "South Africa":           { bg: "#007A4D", accent: "#FFB81C" },
  "Czech Republic":         { bg: "#D7141A", accent: "#FFFFFF" },
  "Canada":                 { bg: "#FF0000", accent: "#FFFFFF" },
  "Switzerland":            { bg: "#FF0000", accent: "#FFFFFF" },
  "Bosnia and Herzegovina": { bg: "#002395", accent: "#FFCC00" },
  "Qatar":                  { bg: "#8D1B3D", accent: "#FFFFFF" },
  "Brazil":                 { bg: "#009C3B", accent: "#FFDF00" },
  "Morocco":                { bg: "#C1272D", accent: "#006233" },
  "Haiti":                  { bg: "#00209F", accent: "#D21034" },
  "Scotland":               { bg: "#003078", accent: "#FFFFFF" },
  "Paraguay":               { bg: "#D52B1E", accent: "#FFFFFF" },
  "United States":          { bg: "#002868", accent: "#BF0A30" },
  "Australia":              { bg: "#00008B", accent: "#FFCD00" },
  "Turkey":                 { bg: "#E30A17", accent: "#FFFFFF" },
  "Germany":                { bg: "#000000", accent: "#FFCC00" },
  "Curaçao":                { bg: "#003DA5", accent: "#F9E814" },
  "Ivory Coast":            { bg: "#F77F00", accent: "#009A44" },
  "Ecuador":                { bg: "#FFD100", accent: "#003DA5" },
  "Netherlands":            { bg: "#FF6600", accent: "#FFFFFF" },
  "Japan":                  { bg: "#BC002D", accent: "#FFFFFF" },
  "Tunisia":                { bg: "#E70013", accent: "#FFFFFF" },
  "Sweden":                 { bg: "#006AA7", accent: "#FECC02" },
  "Belgium":                { bg: "#1A1A1A", accent: "#FDDA24" },
  "Egypt":                  { bg: "#CE1126", accent: "#FFFFFF" },
  "Iran":                   { bg: "#239F40", accent: "#FFFFFF" },
  "New Zealand":            { bg: "#00247D", accent: "#CC142B" },
  "Spain":                  { bg: "#AA151B", accent: "#F1BF00" },
  "Cape Verde":             { bg: "#003893", accent: "#F7D116" },
  "Saudi Arabia":           { bg: "#006C35", accent: "#FFFFFF" },
  "Uruguay":                { bg: "#5AADD3", accent: "#FFFFFF" },
  "France":                 { bg: "#002395", accent: "#FFFFFF" },
  "Senegal":                { bg: "#00853F", accent: "#FDEF42" },
  "Norway":                 { bg: "#EF2B2D", accent: "#FFFFFF" },
  "Iraq":                   { bg: "#CE1126", accent: "#FFFFFF" },
  "Argentina":              { bg: "#74ACDF", accent: "#FFFFFF" },
  "Algeria":                { bg: "#006233", accent: "#FFFFFF" },
  "Austria":                { bg: "#EF3340", accent: "#FFFFFF" },
  "Jordan":                 { bg: "#007A3D", accent: "#FFFFFF" },
  "Portugal":               { bg: "#006600", accent: "#FF2400" },
  "Uzbekistan":             { bg: "#1EB53A", accent: "#FFFFFF" },
  "Colombia":               { bg: "#FCD116", accent: "#003087" },
  "DR Congo":               { bg: "#007FFF", accent: "#CE1126" },
  "England":                { bg: "#CF111A", accent: "#FFFFFF" },
  "Croatia":                { bg: "#FF0000", accent: "#FFFFFF" },
  "Ghana":                  { bg: "#006B3F", accent: "#FCD116" },
  "Panama":                 { bg: "#DA121A", accent: "#FFFFFF" },
};

export const flagSrc = (code, size = 40) => `https://flagcdn.com/w${size}/${code}.png`;
export const displayName = (team) => SHORT_NAMES[team] ?? team;
