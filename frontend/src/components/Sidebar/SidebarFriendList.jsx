import useChangeFriendSidebar from '../../zustand/useChangeFriendSidebar';
import NavbarMobileView from '../Navbar/NavbarMobileView';
import AddFriend from './AddFriend/AddFriend';
import ChangeSidebarButton from './ChangeSidebarFriendButton';
import ReqFriend from './RequestFriend/ReqFriend';

const SidebarFriendList = () => {
  const { isShowAddFriend, isShowNotifications } = useChangeFriendSidebar();

  return (
    <>
      <div className="flex mb-1 w-full justify-center items-center md:hidden">
        <NavbarMobileView />
        <div className="divider px-3 mb-1"></div>
      </div>
      {/* divider */}

      {/* Divider */}
      <div className="flex justify-center items-center p-0 gap-10">
        <ChangeSidebarButton />
      </div>

      <div className="divider px-3 mb-1"></div>

      {/* Content based on active tab */}
      <div className="flex-4 mb-1 shadow-md rounded-md h-full p-2">
        {isShowAddFriend && <AddFriend />}
        {isShowNotifications && <ReqFriend />}
      </div>
    </>
  );
};

export default SidebarFriendList;
