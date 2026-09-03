import { useCallback, useState, useEffect } from 'react';
import { 
  getBlacklistedVehicles, 
  addBlacklistedVehicle, 
  deleteBlacklistedVehicle 
} from '../services/api';

export default function HotlistManager({ isOpen, onClose, onUpdate }) {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    license_plate: '',
    owner_name: '',
    reason: '',
    alert_level: 'INFO',
  });

  const fetchList = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getBlacklistedVehicles();
      setVehicles(data);
    } catch (err) {
      console.error('Failed to fetch hotlist:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isOpen) fetchList();
  }, [isOpen, fetchList]);

  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      await addBlacklistedVehicle(form);
      setForm({ license_plate: '', owner_name: '', reason: '', alert_level: 'INFO' });
      await fetchList();
      onUpdate?.(); // Notify dashboard to refresh analytics
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Remove vehicle from hotlist?')) return;
    try {
      await deleteBlacklistedVehicle(id);
      await fetchList();
      onUpdate?.();
    } catch (err) {
      alert(err.message);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="hotlist-overlay">
      <div className="hotlist-panel">
        <div className="panel-head">
          <div className="panel-title">Hotlist Management</div>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form className="hotlist-form" onSubmit={handleAdd}>
          <div className="form-grid">
            <input 
              placeholder="License Plate" 
              value={form.license_plate} 
              onChange={e => setForm({...form, license_plate: e.target.value.toUpperCase()})} 
              required 
            />
            <input 
              placeholder="Owner Name" 
              value={form.owner_name} 
              onChange={e => setForm({...form, owner_name: e.target.value})} 
              required 
            />
            <select 
              value={form.alert_level} 
              onChange={e => setForm({...form, alert_level: e.target.value})}
            >
              <option value="INFO">INFO</option>
              <option value="WARNING">WARNING</option>
              <option value="CRITICAL">CRITICAL</option>
            </select>
            <input 
              placeholder="Reason / Note" 
              value={form.reason} 
              onChange={e => setForm({...form, reason: e.target.value})} 
              required 
            />
          </div>
          <button type="submit" className="add-btn">ADD TO HOTLIST</button>
        </form>

        <div className="hotlist-table-wrap">
          <table className="hotlist-table">
            <thead>
              <tr>
                <th>Plate</th>
                <th>Owner</th>
                <th>Level</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="4" className="empty">Loading...</td></tr>
              ) : vehicles.length === 0 ? (
                <tr><td colSpan="4" className="empty">No vehicles on hotlist.</td></tr>
              ) : (
                vehicles.map(v => (
                  <tr key={v.id}>
                    <td className="plate-cell">{v.license_plate}</td>
                    <td>{v.owner_name}</td>
                    <td><span className={`level-tag ${v.alert_level}`}>{v.alert_level}</span></td>
                    <td>
                      <button className="del-btn" onClick={() => handleDelete(v.id)}>DELETE</button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
      <style>{`
        .hotlist-overlay {
          position: fixed; top: 0; right: 0; bottom: 0; left: 0;
          background: rgba(0,0,0,0.7); backdrop-filter: blur(4px);
          z-index: 1000; display: flex; justify-content: flex-end;
        }
        .hotlist-panel {
          width: 450px; background: #0b0f19; height: 100%;
          border-left: 1px solid #1e2533; display: flex; flex-direction: column;
          animation: slideIn 0.3s ease-out;
        }
        @keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }
        .panel-head {
          padding: 20px; background: #161b28; display: flex; 
          justify-content: space-between; align-items: center;
          border-bottom: 1px solid #1e2533;
        }
        .panel-title { color: #fff; font-weight: 700; font-size: 18px; }
        .close-btn { 
          background: none; border: none; color: #546e7a; 
          font-size: 28px; cursor: pointer; line-height: 1;
        }
        .close-btn:hover { color: #fff; }
        .hotlist-form { padding: 20px; background: #0f1422; border-bottom: 1px solid #1e2533; }
        .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px; }
        .form-grid input, .form-grid select {
          background: #161b28; border: 1px solid #2d3748; color: #fff;
          padding: 8px; border-radius: 4px; font-size: 13px;
        }
        .form-grid input:focus { border-color: #00e5ff; outline: none; }
        .add-btn {
          width: 100%; padding: 10px; background: #00e5ff; color: #000;
          border: none; border-radius: 4px; font-weight: 700; cursor: pointer;
        }
        .add-btn:hover { background: #00b8cc; }
        .hotlist-table-wrap { flex: 1; overflow-y: auto; padding: 20px; }
        .hotlist-table { width: 100%; border-collapse: collapse; color: #cbd5e0; font-size: 13px; }
        .hotlist-table th { text-align: left; padding: 10px; border-bottom: 2px solid #1e2533; color: #546e7a; }
        .hotlist-table td { padding: 12px 10px; border-bottom: 1px solid #1e2533; }
        .plate-cell { font-family: monospace; font-weight: 700; color: #fff; }
        .level-tag { 
          padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; color: #fff;
        }
        .level-tag.CRITICAL { background: #ff1744; }
        .level-tag.WARNING { background: #ffab00; }
        .level-tag.INFO { background: #00e5ff; color: #000; }
        .del-btn { 
          background: none; border: 1px solid #ff1744; color: #ff1744; 
          padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 11px;
        }
        .del-btn:hover { background: #ff1744; color: #fff; }
        .empty { text-align: center; padding: 40px; opacity: 0.5; }
      `}
      </style>
    </div>
  );
}
