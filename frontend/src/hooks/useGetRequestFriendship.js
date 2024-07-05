import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';

const useGetRequestFriendship = () => {
  const [loading, setLoading] = useState(false);
  const [request, setRequest] = useState([]);

  useEffect(() => {
    const getRequestFriendship = async () => {
      setLoading(true);
      try {
        const res = await fetch('/api/friend-list/request-friend');
        const data = await res.json();
        if (data.error) {
          throw new Error(data.error);
        }
        setRequest(data);
      } catch (error) {
        toast.error(error.message);
      } finally {
        setLoading(false);
      }
    };
    getRequestFriendship();
  }, []);
  return { loading, request };
};

export default useGetRequestFriendship;
