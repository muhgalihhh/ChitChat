import { useState } from 'react';
import toast from 'react-hot-toast';

const useHandleRejectFriendship = () => {
  const [loading, setLoading] = useState(false);

  const rejectFriend = async (friendId) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/friend-list/reject/`, {
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

  return { rejectFriend, loading };
};
export default useHandleRejectFriendship;
