import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./hooks/useAuth";
import SplashScreen from "./screens/auth/SplashScreen";
import LoginScreen from "./screens/auth/LoginScreen";
import RegisterScreen from "./screens/auth/RegisterScreen";
import ForgotPasswordScreen from "./screens/auth/ForgotPasswordScreen";
import MainShell from "./navigation/MainShell";
import ProfilScreen from "./screens/main/ProfilScreen";
import StockScreen from "./screens/main/StockScreen";
import ScanScreen from "./screens/main/ScanScreen";
import RecettesScreen from "./screens/main/RecettesScreen";
import GamificationScreen from "./screens/main/GamificationScreen";

function Protected({ children }) {
  const { isAuthenticated, booting, splashDone } = useAuth();
  if (!splashDone || booting) return <SplashScreen />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return children;
}

function GuestOnly({ children }) {
  const { isAuthenticated, booting, splashDone } = useAuth();
  if (!splashDone || booting) return <SplashScreen />;
  if (isAuthenticated) return <Navigate to="/profil" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <GuestOnly>
            <Navigate to="/login" replace />
          </GuestOnly>
        }
      />
      <Route
        path="/login"
        element={
          <GuestOnly>
            <LoginScreen />
          </GuestOnly>
        }
      />
      <Route
        path="/register"
        element={
          <GuestOnly>
            <RegisterScreen />
          </GuestOnly>
        }
      />
      <Route
        path="/forgot-password"
        element={
          <GuestOnly>
            <ForgotPasswordScreen />
          </GuestOnly>
        }
      />
      <Route
        element={
          <Protected>
            <MainShell />
          </Protected>
        }
      >
        <Route path="/profil" element={<ProfilScreen />} />
        <Route path="/stock" element={<StockScreen />} />
        <Route path="/scan" element={<ScanScreen />} />
        <Route path="/recettes" element={<RecettesScreen />} />
        <Route path="/gamification" element={<GamificationScreen />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}