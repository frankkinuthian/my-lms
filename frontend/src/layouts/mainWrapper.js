import { useEffect, useState } from "react";
import { setUser } from "../utils/auth";

const MainWrapper = ({ children }) => {
  const [loading, setLoading] = useState(true);

  // useEffect hook to handle side effects, such as initializing the user authentication.
  // It runs only once when the component mounts.
  useEffect(() => {
    const handler = async () => {
      setLoading(true);

      await setUser();
      setLoading(false);
    };

    handler();
  }, []);

  // Renders the children only if the loading state is false.
  return <>{loading ? null : children}</>;
};

export default MainWrapper;
