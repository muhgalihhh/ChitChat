import { RiLogoutBoxFill } from 'react-icons/ri';
import useLogout from '../../hooks/useLogout';

const ModalLogout = ({ isOpen, onClose }) => {
  const { loading, logout } = useLogout();
  return (
    <>
      <dialog id="modalLogout" className={`sm:modal-middle modal ${isOpen ? 'modal-open' : 'modal-close'} transition-opacity duration-300 ease-in-out ${isOpen ? 'opacity-100' : 'opacity-0'}`}>
        <div className="modal-box text-slate-900">
          <h3 className="font-bold text-lg">Apakah Anda Yakin?!</h3>
          <p className="py-4">Klik Tombol Untuk Keluar</p>
          <div className="modal-action">
            <button className="btn btn-primary" onClick={onClose}>
              Cancel
            </button>
            <button className="btn btn-error" onClick={onClose}>
              {!loading ? <RiLogoutBoxFill style={{ fontSize: '1.75rem', color: 'ffffff' }} onClick={logout} /> : <span className="loading loading-infinity loading-md"></span>}
            </button>
          </div>
        </div>
      </dialog>
    </>
  );
};

export default ModalLogout;
