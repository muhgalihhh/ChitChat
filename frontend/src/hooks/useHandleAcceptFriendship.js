import { useState } from 'react';
import toast from 'react-hot-toast';

const useHandleAcceptFriendship = () => {
  const [loading, setLoading] = useState(false);

  const acceptFriend = async (friendId) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/friend-list/add/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ friendId }),
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      toast.success('Friend Accepted Successfully');
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };

  return { acceptFriend, loading };
};
export default useHandleAcceptFriendship;
