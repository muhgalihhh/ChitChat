import React, { useState } from 'react';
import MessageContainer from '../../components/Messages/MessageContainer';
import ModalInfoWebsite from '../../components/Modal/ModalInfoWebsite';
import ModalLogout from '../../components/Modal/ModalLogout';
import LogoutButton from '../../components/Navbar/LogoutButton';
import Navbar from '../../components/Navbar/Navbar';
import Sidebar from '../../components/Sidebar/Sidebar';
import SidebarFriendList from '../../components/Sidebar/SidebarFriendList';
import SidebarGroup from '../../components/Sidebar/SidebarGroup';
import { useVisibility } from '../../context/VisibilityContext';
import useChangeSidebar from '../../zustand/useChangeSidebar';

const Home = () => {
  const { isMessageVisible } = useVisibility();
  const { isShowDefault, isShowFriendList, isShowGroupList } = useChangeSidebar();
  const [isModalOpen, setIsModalOpen] = useState(false); // State untuk mengontrol keadaan modal

  const handleModalOpen = () => {
    setIsModalOpen(true);
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
  };

  return (
    <>
      <div className="w-screen h-screen bg-slate-200 flex justify-center items-center relative">
        <div className="fixed z-10 bottom-10 right-10">
          <button className="btn bg-blue-500 text-white py-4 px-4 rounded-lg shadow-md hover:bg-blue-600" onClick={handleModalOpen}>
            <i className="fa-solid fa-info"></i>
          </button>
        </div>
        <div className="w-[90%] h-[90%] relative">
          <div className="fixed left-[1rem] top-[20%] z-1 hidden md:block">
            <div className="flex justify-between items-center h-[90%] text-white relative flex-col">
              <Navbar />
              <div className="flex items-center gap-4">
                <div className="text-sm font-semibold">
                  <LogoutButton onOpenModal={handleModalOpen} />
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white relative z-2 w-full h-full flex rounded-md overflow-hidden border-b-2" style={{ borderRadius: '1rem' }}>
            {isShowDefault && (
              <div className={`md:flex ${isMessageVisible ? 'hidden' : 'block'} flex flex-col w-full bg-white md:flex lg:w-1/3 xl:w-1/4 h-full p-4 border-slate-400`}>
                <Sidebar />
              </div>
            )}
            {isShowFriendList && (
              <div className={`md:flex ${isMessageVisible ? 'hidden' : 'block'} flex flex-col w-full bg-white md:flex lg:w-1/3 xl:w-1/4 h-full p-4 border-slate-400`}>
                <SidebarFriendList />
              </div>
            )}
            {isShowGroupList && (
              <div className={`md:flex ${isMessageVisible ? 'hidden' : 'block'} flex flex-col w-full bg-white md:flex lg:w-1/3 xl:w-1/4 h-full p-4 border-slate-400`}>
                <SidebarGroup />
              </div>
            )}
            <div className={`md:flex ${isMessageVisible ? 'block' : 'hidden'} flex flex-col flex-grow bg-white h-full p-4 border-slate-400 border-l-2 w-full`}>
              <MessageContainer />
            </div>
          </div>
        </div>
      </div>
      {isModalOpen && <ModalInfoWebsite isOpen={isModalOpen} onClose={handleModalClose} />}
      {isModalOpen && <ModalLogout isOpen={isModalOpen} onClose={handleModalClose} />}
    </>
  );
};

export default Home;
