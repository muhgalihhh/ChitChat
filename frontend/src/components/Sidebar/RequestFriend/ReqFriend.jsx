// import React from 'react';
import useGetRequestFriendship from '../../../hooks/useGetRequestFriendship';
import RequestFriendList from './RequestFriendList';

const ReqFriend = () => {
  const { request, loading } = useGetRequestFriendship();
  return (
    <>
      <div className="title">
        <h3 className="text-lg font-semibold">Friend Requests</h3>
      </div>
      <div className="divider px-3 mb-1"></div>
      <div className="flex gap-2 items-center p-2 rounded-md cursor-pointer">
        <RequestFriendList reqFriends={request} loading={loading} />
      </div>
    </>
  );
};

export default ReqFriend;
