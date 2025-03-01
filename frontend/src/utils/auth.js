import { useAuthStore } from "../store/auth";
import axios from "./axios";
import jwt_decode from "jwt-decode";
import Cookie from "js-cookie";
import Swal from "sweetalert2";


// Handles user login by sending a POST request to the server with email and password.
// On success, sets the authentication tokens and alerts the user.
export const login = async (email, password) => {
  try {
    const { data, status } = await axios.post("user/token/", {
      email,
      password,
    });

    if (status === 200) {
      setAuthUser(data.access, data.refresh);
      alert("Login successful");
    }

    return { data, error: null };
  } catch (error) {
    console.log(error);
    return {
      data: null,
      error: error.response.data?.detail || "Something went wrong",
    };
  }
};

// Registers a new user by sending a POST request to the server with user details.
// On success, logs the user in and alerts the user.
export const register = async (full_name, email, password, password2) => {
  try {
    const { data } = await axios.post("user/register/", {
      full_name,
      email,
      password,
      password2,
    });

    await login(email, password);
    alert("Registration successful");
  } catch (error) {
    console.log(error);
    return {
      data: null,
      error: error.response.data?.detail || "Something went wrong",
    };
  }
};

// Logs out the user by removing the access and refresh tokens from cookies and updating the auth store.
export const logout = () => {
  Cookie.remove("access_token");
  Cookie.remove("refresh_token");

  useAuthStore.getState().setAuthUser(null);

  alert("Logout successful");
};

// Sets the user state by checking the access and refresh tokens.
// If the access token is expired, refreshes it using the refresh token.
export const setUser = async () => {
  const access_token = Cookie.get("access_token");
  const refresh_token = Cookie.get("refresh_token");

  if (!access_token || !refresh_token) {
    alert("No token found");
    return;
  }

  if (isAccessTokenExpired(access_token)) {
    const response = getRefreshedToken(refresh_token);
    setAuthUser(response.access, response.refresh);
  } else {
    setAuthUser(access_token, refresh_token);
  }
};

// Sets the authentication tokens in cookies and updates the user state in the auth store.
export const setAuthUser = (access_token, refresh_token) => {
  Cookie.set("access_token", access_token, {
    expires: 1,
    secure: true,
  });
  Cookie.set("refresh_token", refresh_token, {
    expires: 7,
    secure: true,
  });

  const user = jwt_decode(access_token) ?? null;

  if (user) {
    useAuthStore.getState().setUser(user);
  } else {
    setAuthUser.getState().setLoading(false);
  }
};

// Refreshes the access token using the refresh token by sending a POST request to the server.
export const getRefreshedToken = async () => {
  const refresh_token = Cookie.get("refresh_token");

  const response = await axios.post("user/token/refresh/", {
    refresh: refresh_token,
  });

  return response.data;
};

// Checks if the access token is expired by decoding it and comparing the expiration time with the current time.
export const isAccessTokenExpired = async (access_token) => {
  try {
    const decodedToken = jwt_decode(access_token);
    return decodedToken.exp < Date.now() / 1000;
  } catch (error) {
    console.log(error);
    return true;
  }
};