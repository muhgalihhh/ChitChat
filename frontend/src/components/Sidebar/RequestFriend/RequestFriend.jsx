// import React from 'react';

import useHandleAcceptFriendship from '../../../hooks/useHandleAcceptFriendship';
import useHandleRejectFriendship from '../../../hooks/useHandleRejectFriendship';

const RequestFriend = ({ user }) => {
  const { acceptFriend } = useHandleAcceptFriendship();
  const { rejectFriend } = useHandleRejectFriendship();
  const handleAccept = () => {
    acceptFriend(user._id);
  };

  const handleReject = () => {
    rejectFriend(user._id);
  };
  return (
    <>
      <div className={`flex gap-2 items-center p-2 rounded-md cursor-pointer hover:bg-slate-100 border-b-2`}>
        <div className={`avatar`}>
          <div className="w-10 rounded-full">
<<<<<<< HEAD
            <img alt="user avatars" src="https://avatar.iran.liara.run/public/boy?username=panji" />
=======
            <img alt="user avatars" src={user.profilePicture} />
>>>>>>> 66d81a7d1ffb6bfe8379f9644e22ef3460dd7649
          </div>
        </div>
        <div className="flex flex-col flex-1">
          <div className="flex gap-3 justify-between">
<<<<<<< HEAD
            <p className="font-bold text-xs text text-slate-800">Panji</p>
=======
            <p className="font-bold text-xs text text-slate-800">{user.fullName}</p>
>>>>>>> 66d81a7d1ffb6bfe8379f9644e22ef3460dd7649
            <div className="flex gap-2">
              <button className="btn bg-success" onClick={handleAccept}>
                <i className="fa-solid fa-check"></i>
              </button>
              <button className="btn bg-error" onClick={handleReject}>
                {/* detail mata */}
                <i className="fa-solid fa-xmark"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default RequestFriend;
