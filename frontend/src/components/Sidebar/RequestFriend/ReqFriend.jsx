// import React from 'react';
import useGetRequestFriendship from '../../../hooks/useGetRequestFriendship';
import RequestFriendList from './RequestFriendList';

const ReqFriend = () => {
  const { request, loading } = useGetRequestFriendship();
  return (
    <>
      <div className="flex gap-2 items-center p-2 rounded-md cursor-pointer">
        <RequestFriendList reqFriends={request} loading={loading} />
      </div>
    </>
  );
};

export default ReqFriend;
