import React, { useState } from 'react';
import useRequestFriend from '../../../hooks/useRequestFriend';
import ModalInfoUserAdd from '../../Modal/ModalInfoUserAdd';

const FriendRequest = ({ display }) => {
  const { requestFriend } = useRequestFriend();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    requestFriend(display._id);
  };

  const handleOpenModal = (display) => {
    setSelectedUser(display);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedUser(null);
  };

  return (
    <>
      <div className={`flex gap-2 items-center p-2 rounded-md cursor-pointer hover:bg-slate-100 border-b-2 w-full`}>
        <div className={`avatar`}>
          <div className={`avatar`}>
            <div className="w-10 rounded-full">
              <img src={display.profilePicture} alt="user avatars" />
            </div>
          </div>
        </div>
        <div className="flex flex-col flex-1">
          <div className="flex gap-3 justify-between">
            <p className="font-bold text-xs text text-slate-800">{display.fullName}</p>
            <div className="flex gap-2">
              <form onSubmit={handleSubmit}>
                <input type="hidden" value={display._id} name="friendId" readOnly />
                <button className="btn bg-white" type="submit">
                  <i className="fa-solid fa-plus"></i>
                </button>
              </form>
              <button className="btn bg-white" onClick={() => handleOpenModal(display)}>
                <i className="fa-solid fa-eye"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
      <ModalInfoUserAdd isOpen={isModalOpen} onClose={handleCloseModal} user={selectedUser} />
    </>
  );
};

export default FriendRequest;
