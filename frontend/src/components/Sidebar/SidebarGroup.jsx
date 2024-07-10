import NavbarMobileView from '../Navbar/NavbarMobileView';
import GroupContainer from './Group/GroupContainer';
import ChangeSidebarGroupButton from './SidebarGroupButton';

const SidebarGroup = () => {
  return (
    <>
      <div className="flex mb-1 w-full justify-center items-center md:hidden">
        <NavbarMobileView />
        <div className="divider px-3 mb-1"></div>
      </div>
      {/* divider */}
      {/* Divider */}
      <div className="flex justify-center items-center p-0 gap-10">
        <ChangeSidebarGroupButton />
      </div>

      {/* Content based on active tab */}
      <div className="flex-4 mb-1 overflow-y-auto scrollbar shadow-md rounded-md h-full p-2">
        <GroupContainer />
      </div>
    </>
  );
};

export default SidebarGroup;
