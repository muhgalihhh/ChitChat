import React from 'react';

const ModalInfoWebsite = ({ isOpen, onClose }) => {
  const creators = [
    { name: 'Adnan', role: 'Manusia Ungsut', avatar: 'https://api.dicebear.com/9.x/adventurer/svg?seed=Coco', github: 'https://github.com/adnanfito/' },
    { name: 'Galih', role: 'Cucu pak dirman', avatar: 'https://api.dicebear.com/9.x/adventurer/svg?seed=Boo', github: 'https://github.com/muhgalihhh/' },
  ];

  return (
    <dialog id="modalInfoWebsite" className={`modal ${isOpen ? 'modal-open' : 'modal-close'} transition-opacity duration-300 ease-in-out ${isOpen ? 'opacity-100' : 'opacity-0'}`}>
      <div className="modal-box p-10 bg-white rounded-lg shadow-lg w-6/12 max-w-5xl sm:w-10/12 md:w-9/12 lg:w-8/12 xl:w-7/12">
        <div className="modal-header flex justify-between items-center">
          <div className="title flex gap-2">
            <h3 className="text-lg font-bold text-gray-800">About This Website</h3>
            <span className="loading loading-infinity"></span>
          </div>
          <button className="modal-close" aria-label="Close modal" onClick={onClose}>
            <svg className="w-6 h-6 text-gray-600 hover:text-gray-800" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div className="modal-body mt-4 text-gray-700">
          <p className="mb-5">This website is built by:</p>
          <div className="flex gap-4 mb-4">
            {creators.map((creator, index) => (
              <div key={index} className="flex items-center justify-between gap-4 shadow-sm border rounded-md px-3">
                <div className="flex gap-2 items-center">
                  <img className="w-16 h-16 rounded-full" src={creator.avatar} alt={creator.name} />
                  <p className="font-semibold">{creator.name}</p>
                  <p className="text-sm">{creator.role}</p>
                </div>
                <a href={creator.github} target="_blank" rel="noreferrer" className="hover:bg-slate-300 px-3 py-2 rounded-full">
                  <i className="fa-brands fa-github"></i>
                </a>
              </div>
            ))}
          </div>
          <p className="mb-5">This website is built using the following technologies:</p>
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center">
              <img className="w-12" src="https://ionicframework.com/docs/icons/logo-react-icon.png" alt="React" />
              <span className="ml-2">React</span>
            </div>
            <div className="flex items-center">
              <img className="w-12" src="https://static-00.iconduck.com/assets.00/mongodb-original-wordmark-icon-1008x1024-ebdbwvkl.png" alt="MongoDB" />
              <span className="ml-2">MongoDB</span>
            </div>
            <div className="flex items-center">
              <img className="w-12" src="https://www.simplilearn.com/ice9/tools_covered/ExpressJS-logo.png" alt="Express" />
              <span className="ml-2">Express</span>
            </div>
            <div className="flex items-center">
              <img className="w-12" src="https://static-00.iconduck.com/assets.00/node-js-icon-454x512-nztofx17.png" alt="Node.js" />
              <span className="ml-2">Node.js</span>
            </div>
            <div className="flex items-center">
              <img className="w-12" src="https://static-00.iconduck.com/assets.00/socket-io-icon-1024x1023-qk25cbjb.png" alt="Socket.js" />
              <span className="ml-2">Socket.js</span>
            </div>
            <div className="flex items-center">
              <img className="w-12" src="https://static-00.iconduck.com/assets.00/tailwind-css-icon-2048x1229-u8dzt4uh.png" alt="Tailwind CSS" />
              <span className="ml-2">Tailwind CSS</span>
            </div>
          </div>
        </div>
      </div>
    </dialog>
  );
};

export default ModalInfoWebsite;
