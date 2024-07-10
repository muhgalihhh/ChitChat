import { useState } from 'react';
import useChangeSidebar from '../../zustand/useChangeSidebar';
import ModalLogout from '../Modal/ModalLogout';
import LogoutButton from './LogoutButton';

const NavbarMobileView = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { showDefault, showFriendList, showGroupList, activeTab } = useChangeSidebar();

  const handleOpenModal = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  return (
    <div className="flex items-center gap-4 justify-around w-full">
      <button className={`text-sm font-semibold py-2 px-2 rounded-md ${activeTab === 'default' && 'bg-gray-200'}`} onClick={showDefault}>
        <i className="fa-solid fa-comments"></i>
      </button>
      <button className={`text-sm font-semibold py-2 px-2 rounded-md ${activeTab === 'friends' && 'bg-gray-200'}`} onClick={showFriendList}>
        <i className="fa-solid fa-people-group"></i>
      </button>
      <button className={`text-sm font-semibold py-2 px-2 rounded-md ${activeTab === 'groups' && 'bg-gray-200'}`} onClick={showGroupList}>
        <i className="fa-solid fa-address-book"></i>
      </button>
      <div className="text-sm font-semibold">
        <LogoutButton onOpenModal={handleOpenModal} />
        <ModalLogout isOpen={isModalOpen} onClose={handleCloseModal} />
      </div>
    </div>
  );
};

export default NavbarMobileView;
