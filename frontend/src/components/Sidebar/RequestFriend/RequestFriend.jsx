import React, { useState } from 'react';
import useHandleAcceptFriendship from '../../../hooks/useHandleAcceptFriendship';
import useHandleRejectFriendship from '../../../hooks/useHandleRejectFriendship';
import Modal from '../../Modal/ModalInfoUser';

const RequestFriend = ({ user }) => {
  const { acceptFriend } = useHandleAcceptFriendship();
  const { rejectFriend } = useHandleRejectFriendship();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  const handleAccept = () => {
    acceptFriend(user._id);
  };

  const handleReject = () => {
    rejectFriend(user._id);
  };

  const handleOpenModal = (user) => {
    setSelectedUser(user);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedUser(null);
  };

  return (
    <>
      <div className={`flex gap-2 items-center p-2 rounded-md cursor-pointer hover:bg-slate-100 border-b-2`}>
        <div className={`avatar`}>
          <div className="w-10 rounded-full">
            <img alt="user avatars" src={user.profilePicture} />
          </div>
        </div>
        <div className="flex flex-col flex-1">
          <div className="flex gap-3 justify-between">
            <p className="font-bold text-xs text text-slate-800">{user.fullName}</p>
            <div className="flex gap-2">
              <button className="btn bg-success" onClick={handleAccept}>
                <i className="fa-solid fa-check"></i>
              </button>
              <button className="btn bg-error" onClick={handleReject}>
                <i className="fa-solid fa-xmark"></i>
              </button>
              <button className="btn bg-info" onClick={() => handleOpenModal(user)}>
                <i className="fa-solid fa-info-circle"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
      {isModalOpen && <Modal isOpen={isModalOpen} onClose={handleCloseModal} user={selectedUser} />}
    </>
  );
};

export default RequestFriend;
