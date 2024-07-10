import { useState } from 'react';
import { useSocketContext } from '../../context/SocketContext';
import { useVisibility } from '../../context/VisibilityContext';
import useConversation from '../../zustand/useConversation';
import Modal from '../Modal/ModalInfoUser';

const Conversation = ({ conversation, lastIdx }) => {
  const { selectedConversation, setSelectedConversation } = useConversation();
  const isSelected = selectedConversation?._id === conversation._id;
  const { onlineUsers } = useSocketContext();
  const isOnline = onlineUsers.includes(conversation._id);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const { showMessages } = useVisibility();

  const handleOpenModal = (user) => {
    setSelectedUser({ ...user, isOnline });
    setIsModalOpen(true);
  };

  const handleClick = () => {
    setSelectedConversation(conversation);
    showMessages();
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedUser(null);
  };

  return (
    <>
      <div className={`flex gap-2 items-center p-2 rounded-md cursor-pointer w-full hover:bg-slate-100 ${isSelected ? 'bg-slate-200' : 'bg-white'}`} onClick={handleClick}>
        <div className={`avatar ${isOnline ? 'online' : 'offline'}`}>
          <div className="w-10 rounded-full">
            <img src={conversation.profilePicture} alt="user avatars" />
          </div>
        </div>
        <div className="flex flex-col flex-1">
          <div className="flex gap-3 justify-between">
            <p className="font-bold text-xs text text-slate-800">{conversation.fullName}</p>
            <button className="btn bg-white" onClick={() => handleOpenModal(conversation)}>
              <i className="fa-solid fa-ellipsis-vertical"></i>
            </button>
          </div>
        </div>
      </div>
      {!lastIdx && <div className="divider my-0 py-0 h-1"></div>}
      <Modal isOpen={isModalOpen} onClose={handleCloseModal} user={selectedUser} />
    </>
  );
};

export default Conversation;
