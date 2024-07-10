const ModalInfoUserAdd = ({ isOpen, onClose, user }) => {
  if (!user) return null;

  return (
    <dialog id="modalInfoUser" className={`modal ${isOpen ? 'modal-open' : 'modal-close'} transition-opacity duration-300 ease-in-out ${isOpen ? 'opacity-100' : 'opacity-0'}`}>
      <div className="modal-box bg-white p-6 rounded-lg shadow-xl">
        <h3 className="font-bold text-2xl mb-6 text-center">User Information</h3>
        <div className="flex flex-col items-center mb-6">
          <div className={`avatar mb-4`}>
            <div className="w-24 h-24 rounded-full ring ring-primary ring-offset-base-100 ring-offset-2 overflow-hidden">
              <img src={user.profilePicture} alt={`${user.fullName} profile`} />
            </div>
          </div>
          <div className="text-center">
            <p className="text-2xl font-semibold mb-1">{user.fullName}</p>
            <p className="text-md text-gray-500">{user.email}</p>
          </div>
        </div>
        <div className="py-2 text-center">
          <strong className="block text-gray-700">Gender:</strong> <span className="text-gray-800">{user.gender}</span>
        </div>
        <div className="py-2 text-center">
          <strong className="block text-gray-700">Status:</strong>
          Add Dulu Bang
        </div>
        <div className="modal-action flex justify-center mt-6">
          <button className="btn btn-neutral px-6 py-2 rounded-full" onClick={onClose}>
            <i className="fa-solid fa-xmark-circle"></i>
            Close
          </button>
        </div>
      </div>
    </dialog>
  );
};

export default ModalInfoUserAdd;
