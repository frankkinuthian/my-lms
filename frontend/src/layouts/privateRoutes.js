import { Navigate } from "react-router-dom";
import { useAuthStore } from "../store/auth";

const PrivateRoute = ({ children }) => {
  // # Use the useAuthStore to check if the user is logged in
  const loggedIn = useAuthStore((state) => state.isLoggedIn)();

  //    Conditionally render the children
  return loggedIn ? children : <Navigate to="/login" />;
};

export default PrivateRoute;
