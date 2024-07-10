import NavbarMobileView from '../Navbar/NavbarMobileView';
import ConversationList from './ConversationList';
import SearchInput from './SearchInput';

const Sidebar = () => {
  return (
    <>
      <div className="flex mb-1 w-full justify-center items-center md:hidden">
        <NavbarMobileView />
        <div className="divider px-3 mb-1"></div>
      </div>

      {/* Divider */}
      {/* SearchInput Component */}
      <div className="mb-1 w-full">
        <SearchInput />
      </div>

      <div className="divider px-3 mb-1"></div>

      {/* NavbarMobileView Component - only visible on mobile screens */}

      {/* ConversationList Component */}
      <div className="flex-4 mb-1 overflow-y-auto scrollbar shadow-md rounded-md h-full p-2 w-full">
        <ConversationList />
      </div>

      {/* Divider */}
      <div className="divider px-3 mb-4"></div>

      {/* LogoutButton Component */}
    </>
  );
};

export default Sidebar;
