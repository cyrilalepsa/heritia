import { NavLink } from "react-router-dom";
import { NAV_TABS } from "../config/constants";

function Icon({ name }) {
  switch (name) {
    case "user":
      return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
          <circle cx="12" cy="8" r="3.2" />
          <path d="M5 19.2c1.6-3.2 4-4.8 7-4.8s5.4 1.6 7 4.8" />
        </svg>
      );
    case "box":
      return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
          <path d="M4 8l8-4 8 4v8l-8 4-8-4V8z" />
          <path d="M12 12v8M4 8l8 4 8-4" />
        </svg>
      );
    case "scan":
      return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
          <path d="M7 4H5a1 1 0 0 0-1 1v2M17 4h2a1 1 0 0 1 1 1v2M7 20H5a1 1 0 0 1-1-1v-2M17 20h2a1 1 0 0 0 1-1v-2M4 12h16" />
        </svg>
      );
    case "book":
      return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
          <path d="M5 5.5A2.5 2.5 0 0 1 7.5 3H19v16H7.5A2.5 2.5 0 0 0 5 21.5V5.5z" />
          <path d="M5 18.5A2.5 2.5 0 0 1 7.5 16H19" />
        </svg>
      );
    case "trophy":
      return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
          <path d="M8 4h8v5a4 4 0 0 1-8 0V4z" />
          <path d="M8 6H5a2 2 0 0 0 2 4M16 6h3a2 2 0 0 1-2 4M10 17h4M12 13v4M9 20h6" />
        </svg>
      );
    default:
      return null;
  }
}

export default function BottomNav() {
  return (
    <nav className="bottom-nav" aria-label="Navigation principale HERITIA">
      {NAV_TABS.map((tab) => (
        <NavLink
          key={tab.path}
          to={tab.path}
          className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
        >
          <Icon name={tab.icon} />
          <span>{tab.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}