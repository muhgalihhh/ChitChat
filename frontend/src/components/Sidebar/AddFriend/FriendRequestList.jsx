// import React from 'react';
import FriendRequest from './FriendRequest';

const FriendRequestList = ({ friends, loading }) => {
  if (!friends || friends.length === 0) {
    return (
      <div className="container">
        <h1 className="text-2xl font-semibold text-center mt-10">No Users</h1>
      </div>
    );
  }

  return (
    <div className="p-2 flex flex-col max-h-80 overflow-y-auto mt-5 w-full">
      {friends.map((friend) => (
        <FriendRequest key={friend._id} display={friend} />
      ))}
      {loading ? <span className="loading loading-infinity loading-md"></span> : null}
    </div>
  );
};

export default FriendRequestList;
