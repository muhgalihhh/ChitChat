import React from 'react';

const ModalDetailGroup = ({ isOpen, onClose, group }) => {
  if (!isOpen) return null;

  const handleLeaveGroup = () => {
    // Logic untuk meninggalkan grup
    console.log(`Leave group ${group.name}`);
    onClose(); // Tutup modal setelah meninggalkan grup
  };

  const handleRemoveParticipant = (participantId) => {
    // Logic untuk menghapus peserta dari grup
    alert(`Remove participant ${participantId} from group ${group.name}`);
    // Implement logic for removing participant
  };

  return (
    <dialog id="modalDetailGroup" className="modal modal-open transition-opacity duration-300 ease-in-out opacity-100 sm:modal-middle">
      <div className="modal-box bg-white p-6 rounded-lg shadow-xl">
        <h3 className="font-bold text-2xl mb-6 text-center">Group Details</h3>
        <div className="mb-4">
          <label htmlFor="groupName" className="block text-gray-700 font-semibold mb-2">
            Group Name
          </label>
          <div className="bg-gray-100 p-2 rounded-md">{group.name}</div>
        </div>
        <div className="mb-4">
          <label htmlFor="groupDescription" className="block text-gray-700 font-semibold mb-2">
            Group Description
          </label>
          <div className="bg-gray-100 p-2 rounded-md">{group.description}</div>
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 font-semibold mb-2">Participants</label>
          <div className="overflow-y-auto max-h-60">
            {group.participants.map((participant) => (
              <div key={participant.id} className="flex items-center mb-2">
                <div className="bg-gray-100 p-2 rounded-md flex justify-between w-full">
                  {participant.name}
                  <button className="bg-red-500 p-1 rounded-full text-white" onClick={() => handleRemoveParticipant(participant.id)}>
                    <i className="fa-solid fa-minus"></i>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="modal-action flex justify-center mt-6">
          <button className="btn btn-primary px-6 py-2 rounded-full mr-2" onClick={handleLeaveGroup}>
            <i className="fa-solid fa-sign-out"></i>
            Leave
          </button>
          <button className="btn btn-neutral px-6 py-2 rounded-full" onClick={onClose}>
            <i className="fa-solid fa-xmark-circle"></i>
            Close
          </button>
        </div>
      </div>
    </dialog>
  );
};

export default ModalDetailGroup;
