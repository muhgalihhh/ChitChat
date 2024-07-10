import useChangeSidebar from '../../zustand/useChangeSidebar';
const Navbar = () => {
  const { showDefault, showFriendList, showGroupList, activeTab } = useChangeSidebar();

  return (
    <>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-4 flex-col">
          <button
            className={`text-sm font-semibold py-4 pl-4 pr-6 rounded-md hover:bg-slate-400 hover:text-slate-600 hover:shadow-md ${
              activeTab === 'default' ? 'bg-slate-600 text-white' : 'bg-slate-800'
            }`}
            onClick={showDefault}
          >
            <i className="fa-solid fa-comments"></i>
          </button>
          <button
            className={`text-sm font-semibold py-4 pl-4 pr-6 rounded-md hover:bg-slate-400 hover:text-slate-600 hover:shadow-md ${
              activeTab === 'friends' ? 'bg-slate-600 text-white' : 'bg-slate-800'
            }`}
            onClick={showFriendList}
          >
            <i className="fa-solid fa-people-group"></i>
          </button>
          <button
            className={`text-sm font-semibold py-4 pl-[1.2rem] pr-6 rounded-md hover:bg-slate-400 hover:text-slate-600 hover:shadow-md ${
              activeTab === 'groups' ? 'bg-slate-600 text-white' : 'bg-slate-800'
            }`}
            onClick={showGroupList}
          >
            <i className="fa-solid fa-address-book"></i>
          </button>
        </div>
      </div>
    </>
  );
};

export default Navbar;
