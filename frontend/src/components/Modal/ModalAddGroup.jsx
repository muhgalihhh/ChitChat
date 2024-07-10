import React, { useState } from 'react';

const ModalAddGroup = ({ isOpen, onClose, participants }) => {
  const [groupName, setGroupName] = useState('');
  const [groupDescription, setGroupDescription] = useState('');
  const [selectedParticipants, setSelectedParticipants] = useState([]);

  const handleParticipantChange = (e) => {
    const { value, checked } = e.target;
    setSelectedParticipants((prev) => (checked ? [...prev, value] : prev.filter((id) => id !== value)));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Add your form submission logic here
    console.log({ groupName, groupDescription, selectedParticipants });
    onClose();
  };

  return (
    <dialog id="modalAddGroup" className={`modal ${isOpen ? 'modal-open' : 'modal-close'} transition-opacity duration-300 ease-in-out ${isOpen ? 'opacity-100' : 'opacity-0'} sm:modal-middle`}>
      <div className="modal-box bg-white p-6 rounded-lg shadow-xl">
        <h3 className="font-bold text-2xl mb-6 text-center">Add Group</h3>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="groupName" className="block text-gray-700 font-semibold mb-2">
              Group Name
            </label>
            <input type="text" id="groupName" className="input input-bordered w-full" value={groupName} onChange={(e) => setGroupName(e.target.value)} required />
          </div>
          <div className="mb-4">
            <label htmlFor="groupDescription" className="block text-gray-700 font-semibold mb-2">
              Group Description
            </label>
            <textarea id="groupDescription" className="textarea textarea-bordered w-full" value={groupDescription} onChange={(e) => setGroupDescription(e.target.value)} required />
          </div>
          <div className="mb-4" style={{ maxHeight: '300px', overflowY: 'auto' }}>
            <label className="block text-gray-700 font-semibold mb-2">Select Participants</label>
            {participants.map((participant) => (
              <div key={participant.id} className="flex items-center mb-2">
                <input type="checkbox" id={`participant-${participant.id}`} value={participant.id} onChange={handleParticipantChange} className="checkbox checkbox-primary" />
                <label htmlFor={`participant-${participant.id}`} className="ml-2">
                  {participant.name}
                </label>
              </div>
            ))}
          </div>
          <div className="modal-action flex justify-center mt-6">
            <button type="button" className="btn btn-neutral px-6 py-2 rounded-full mr-2" onClick={onClose}>
              <i className="fa-solid fa-xmark-circle"></i>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary px-6 py-2 rounded-full">
              <i className="fa-solid fa-check-circle"></i>
              Add Group
            </button>
          </div>
        </form>
      </div>
    </dialog>
  );
};

export default ModalAddGroup;
