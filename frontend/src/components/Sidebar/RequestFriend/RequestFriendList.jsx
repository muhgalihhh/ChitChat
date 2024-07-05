// import React from 'react';
import RequestFriend from './RequestFriend';

const RequestFriendList = ({ reqFriends, loading }) => {
  if (!reqFriends) {
    return <div className="container"></div>;
  }

  return (
    <div className="p-1 flex flex-col">
      {reqFriends.map((friend) => (
        <RequestFriend key={friend._id} user={friend} />
      ))}
      {loading ? <span className="loading loading-infinity loading-md"></span> : null}
    </div>
  );
};

export default RequestFriendList;
