import axios from "axios";
import { getRefreshedToken, isAccessTokenExpired, setAuthUser } from "./auth";
import Cookie from "js-cookie";
import { API_BASE_URL } from "./constants";

// Custom hook to create an Axios instance with token refresh logic
const useAxios = () => {
  const accessToken = Cookie.get("access_token");
  const refreshToken = Cookie.get("refresh_token");

  // Create an Axios instance with base URL and authorization header
  const axiosInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  // Intercept request to check if the access token is expired and refresh it if necessary
  axiosInstance.interceptors.request.use(async (req) => {
    if (!isAccessTokenExpired) {
      return req;
    }

    const response = await getRefreshedToken(refreshToken);
    setAuthUser(response.access, response.refresh);

    req.headers.Authorization = `Bearer ${response.data?.access}`;
    return req;
  });

  return axiosInstance;
};

export default useAxios;
