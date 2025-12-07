import React, { useState, useEffect, useMemo } from 'react';
import {
  Users, Upload, Trash2, Plus, RefreshCw, BarChart, AlertCircle, FileText,
  Search, ArrowUpDown, ArrowUp, ArrowDown, Moon, Sun, Filter, X, ChevronDown, ChevronUp
} from 'lucide-react';

// 設定後端 API 位置 (依據環境自動判斷)
const getApiBaseUrl = () => {
  if (window.location.host === 'localhost:8000') return '';
  return 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

// 模擬數據 (當後端無法連接時使用)
const MOCK_USERS = [
  { name: 'Bulbasaur', age: 14 }, { name: 'Ivysaur', age: 13 }, { name: 'Venusaur', age: 24 },
  { name: 'Charmander', age: 22 }, { name: 'Charmeleon', age: 13 }, { name: 'Charizard', age: 36 },
  { name: 'Squirtle', age: 10 }, { name: 'Wartortle', age: 18 }, { name: 'Blastoise', age: 45 },
  { name: 'Pikachu', age: 5 }, { name: 'Raichu', age: 28 }, { name: 'Mewtwo', age: 100 },
  { name: 'Snorlax', age: 35 }, { name: 'Gengar', age: 55 }, { name: 'Eevee', age: 3 },
  { name: 'Dragonite', age: 40 }, { name: 'Mew', age: 150 }, { name: 'Celebi', age: 99 }
];

const MOCK_STATS = {
  'B': 24.3, 'I': 13.0, 'V': 24.0, 'C': 23.6, 'S': 22.5, 'W': 18.0, 'P': 5.0, 'R': 28.0,
  'M': 100.0, 'G': 55.0, 'E': 3.0, 'D': 40.0, 'X': 99.0, 'Y': 12.0, 'Z': 88.0
};

const App = () => {
  // --- 1. 核心資料與狀態 ---
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isDemoMode, setIsDemoMode] = useState(false);

  // --- 2. UI 互動狀態 ---
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [searchTerm, setSearchTerm] = useState('');
  const [ageRange, setAgeRange] = useState({ min: '', max: '' });
  const [showAllStats, setShowAllStats] = useState(false); // [新增] 控制是否顯示完整排名

  // 表單與上傳狀態
  const [newUser, setNewUser] = useState({ name: '', age: '' });
  const [file, setFile] = useState(null);
  const [uploadMsg, setUploadMsg] = useState('');

  // 初始化載入數據
  useEffect(() => {
    fetchAllData();
  }, []);

  // --- API 呼叫邏輯 ---
  const fetchAllData = async () => {
    setLoading(true);
    setError(null);
    try {
      await Promise.all([fetchUsers(), fetchStats()]);
      setIsDemoMode(false);
    } catch (err) {
      console.warn("Backend connection failed, switching to Mock Data mode.", err);
      setUsers(MOCK_USERS);
      setStats(MOCK_STATS);
      setIsDemoMode(true);
      setError("無法連接後端 API，目前顯示為展示數據 (Mock Data)。");
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    const res = await fetch(`${API_BASE_URL}/users`);
    if (!res.ok) throw new Error('Failed to fetch users');
    const data = await res.json();
    setUsers(data);
  };

  const fetchStats = async () => {
    const res = await fetch(`${API_BASE_URL}/users/stats/age-group`);
    if (!res.ok) throw new Error('Failed to fetch stats');
    const data = await res.json();
    setStats(data);
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    if (isDemoMode) {
      alert("展示模式下無法實際寫入資料庫，但會模擬新增效果。");
      const mockNewUser = { name: newUser.name, age: parseInt(newUser.age) };
      setUsers([...users, mockNewUser]);
      setNewUser({ name: '', age: '' });
      return;
    }

    try {
      const res = await fetch(`${API_BASE_URL}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newUser.name, age: parseInt(newUser.age) })
      });

      if (res.status === 409) {
        alert('建立失敗：使用者名稱已存在 (Conflict)');
        return;
      }
      if (res.status === 422) {
        const errData = await res.json();
        alert(`驗證錯誤：${errData.detail[0]?.msg || JSON.stringify(errData)}`);
        return;
      }
      if (!res.ok) throw new Error('Create failed');

      setNewUser({ name: '', age: '' });
      fetchAllData();
    } catch (err) {
      alert('發生錯誤：' + err.message);
    }
  };

  const handleDeleteUser = async (name) => {
    if (!confirm(`確定要刪除使用者 ${name} 嗎?`)) return;

    if (isDemoMode) {
      setUsers(users.filter(u => u.name !== name));
      return;
    }

    try {
      const res = await fetch(`${API_BASE_URL}/users/${name}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Delete failed');
      fetchAllData();
    } catch (err) {
      alert('刪除失敗：' + err.message);
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      alert("請先選擇 CSV 檔案");
      return;
    }

    if (isDemoMode) {
      alert("展示模式下無法實際上傳檔案。");
      setUploadMsg("模擬上傳成功！");
      setFile(null);
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploadMsg('上傳處理中...');
      const res = await fetch(`${API_BASE_URL}/users/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Upload failed');
      }

      const data = await res.json();
      setUploadMsg(`成功新增 ${data.added_count} 筆資料！`);
      setFile(null);
      document.getElementById('csvInput').value = "";
      fetchAllData();
    } catch (err) {
      setUploadMsg('上傳失敗：' + err.message);
    }
  };

  // --- 3. 排序與篩選邏輯 (前端處理) ---
  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const processedUsers = useMemo(() => {
    let result = [...users];

    // A. 篩選 (Filter)
    if (searchTerm) {
      result = result.filter(u => u.name.toLowerCase().includes(searchTerm.toLowerCase()));
    }
    if (ageRange.min !== '') {
      result = result.filter(u => u.age >= parseInt(ageRange.min));
    }
    if (ageRange.max !== '') {
      result = result.filter(u => u.age <= parseInt(ageRange.max));
    }

    // B. 排序 (Sort)
    if (sortConfig.key) {
      result.sort((a, b) => {
        if (a[sortConfig.key] < b[sortConfig.key]) {
          return sortConfig.direction === 'asc' ? -1 : 1;
        }
        if (a[sortConfig.key] > b[sortConfig.key]) {
          return sortConfig.direction === 'asc' ? 1 : -1;
        }
        return 0;
      });
    }
    return result;
  }, [users, sortConfig, searchTerm, ageRange]);

  // --- 4. 統計圖表資料處理 (已加入顯示完整排名邏輯) ---
  const displayStats = useMemo(() => {
    // 1. 轉換為陣列並排序
    const statsArray = Object.entries(stats).map(([group, avg]) => ({
      group,
      avg: parseFloat(avg)
    })).sort((a, b) => b.avg - a.avg);

    // 2. 計算最大值 (用於繪圖比例)
    const maxVal = statsArray.length > 0 ? statsArray[0].avg : 0;

    // 3. 根據 showAllStats 決定回傳全部或前 5 名
    const data = showAllStats ? statsArray : statsArray.slice(0, 5);

    return { data, maxVal, totalCount: statsArray.length };
  }, [stats, showAllStats]);


  // --- Render Helpers ---
  const SortIcon = ({ columnKey }) => {
    if (sortConfig.key !== columnKey) return <ArrowUpDown size={14} className="opacity-30" />;
    return sortConfig.direction === 'asc'
      ? <ArrowUp size={14} className="text-blue-500" />
      : <ArrowDown size={14} className="text-blue-500" />;
  };

  return (
    <div className={isDarkMode ? 'dark' : ''}>
      <div className="min-h-screen transition-colors duration-300 font-sans bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-100 p-4 md:p-8">
        <div className="max-w-7xl mx-auto space-y-6">

          {/* Header */}
          <header className="flex flex-col md:flex-row justify-between items-center bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border-l-4 border-blue-600 dark:border-blue-500 transition-colors">
            <div className="mb-4 md:mb-0">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <Users className="text-blue-600 dark:text-blue-400" />
                User Management System
              </h1>
              <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Backend Hands-on Practice Interface</p>
            </div>

            <div className="flex gap-3 items-center">
              <button
                onClick={() => setIsDarkMode(!isDarkMode)}
                className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-gray-600 dark:text-gray-300"
                title="切換深色模式"
              >
                {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
              </button>

              <a
                href="/docs"
                target="_blank"
                className="flex items-center gap-2 px-4 py-2 bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-400 hover:bg-green-100 dark:hover:bg-green-900/50 rounded-lg transition-colors text-sm font-medium border border-green-200 dark:border-green-800"
              >
                <FileText size={16} />
                <span className="hidden sm:inline">Swagger Docs</span>
              </a>

              <button
                onClick={fetchAllData}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors text-sm font-medium text-gray-700 dark:text-gray-200"
              >
                <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
                <span className="hidden sm:inline">刷新</span>
              </button>
            </div>
          </header>

          {/* Error Message */}
          {error && (
            <div className="bg-yellow-50 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200 p-4 rounded-lg flex items-center gap-3 border border-yellow-200 dark:border-yellow-800">
              <AlertCircle size={20} />
              <span>{error}</span>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

            {/* Left Column: Actions & Stats */}
            <div className="space-y-6">

              {/* 1. Create User Card */}
              <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm transition-colors">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2 dark:text-white">
                  <Plus size={20} className="text-green-600 dark:text-green-400" /> 新增使用者
                </h2>
                <form onSubmit={handleCreateUser} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">姓名 (Name)</label>
                    <input
                      type="text"
                      required
                      placeholder="Ex: Pikachu"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                      value={newUser.name}
                      onChange={e => setNewUser({ ...newUser, name: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">年齡 (Age)</label>
                    <input
                      type="number"
                      required
                      min="0"
                      max="150"
                      placeholder="Ex: 25"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                      value={newUser.age}
                      onChange={e => setNewUser({ ...newUser, age: e.target.value })}
                    />
                  </div>
                  <button
                    type="submit"
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors shadow-sm"
                  >
                    建立使用者
                  </button>
                </form>
              </div>

              {/* 2. CSV Upload Card */}
              <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm transition-colors">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2 dark:text-white">
                  <Upload size={20} className="text-purple-600 dark:text-purple-400" /> 批次上傳 (CSV)
                </h2>
                <form onSubmit={handleFileUpload} className="space-y-4">
                  <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                    <input
                      id="csvInput"
                      type="file"
                      accept=".csv"
                      onChange={e => setFile(e.target.files[0])}
                      className="hidden"
                    />
                    <label htmlFor="csvInput" className="cursor-pointer flex flex-col items-center">
                      <FileText className="text-gray-400 mb-2" size={32} />
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {file ? file.name : "點擊選擇檔案"}
                      </span>
                    </label>
                  </div>
                  <button
                    type="submit"
                    disabled={!file}
                    className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-purple-300 dark:disabled:bg-purple-900 text-white font-medium py-2 px-4 rounded-lg transition-colors shadow-sm"
                  >
                    開始上傳
                  </button>
                  {uploadMsg && <p className="text-sm text-center text-gray-600 dark:text-gray-400">{uploadMsg}</p>}
                </form>
              </div>

              {/* 3. Stats Card (Ranking Chart with Toggle) */}
              <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm transition-colors flex flex-col">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-lg font-semibold flex items-center gap-2 dark:text-white">
                    <BarChart size={20} className="text-orange-600 dark:text-orange-400" />
                    {showAllStats ? '分組平均年齡排名' : '平均年齡 Top 5'}
                  </h2>
                  <span className="text-xs text-gray-500 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded-full">
                    Total: {displayStats.totalCount} Groups
                  </span>
                </div>

                {/* Scrollable Area for Chart */}
                <div className="space-y-4 flex-1 overflow-y-auto max-h-[300px] custom-scrollbar pr-2">
                  {displayStats.data.length === 0 ? (
                    <p className="text-gray-400 text-sm text-center py-4">尚無統計數據</p>
                  ) : (
                    displayStats.data.map((item, index) => (
                      <div key={item.group} className="space-y-1">
                        <div className="flex justify-between text-sm">
                          <span className="font-bold text-gray-700 dark:text-gray-300 flex items-center gap-2">
                            <span className={`
                              w-6 h-6 rounded-full flex items-center justify-center text-xs
                              ${index < 3
                                ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300'
                                : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'}
                            `}>
                              {index + 1}
                            </span>
                            Group {item.group}
                          </span>
                          <span className="text-gray-500 dark:text-gray-400">{item.avg.toFixed(1)} 歲</span>
                        </div>
                        {/* Bar Chart Visual */}
                        <div className="h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-orange-500 dark:bg-orange-400 rounded-full transition-all duration-500"
                            style={{ width: `${(item.avg / displayStats.maxVal) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {/* Show All Toggle Button */}
                {displayStats.totalCount > 5 && (
                  <button
                    onClick={() => setShowAllStats(!showAllStats)}
                    className="mt-4 w-full flex items-center justify-center gap-2 text-sm text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 py-2 rounded-lg transition-colors border border-dashed border-blue-200 dark:border-blue-800"
                  >
                    {showAllStats ? (
                      <>收合排名 <ChevronUp size={16} /></>
                    ) : (
                      <>顯示完整排名 <ChevronDown size={16} /></>
                    )}
                  </button>
                )}
              </div>

            </div>

            {/* Right Column: User List (with Search & Sort) */}
            <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl shadow-sm overflow-hidden flex flex-col h-[850px] transition-colors">

              {/* Filter & Search Bar */}
              <div className="p-4 border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 space-y-3">
                <div className="flex flex-col sm:flex-row gap-3">
                  {/* Name Search */}
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
                    <input
                      type="text"
                      placeholder="搜尋姓名..."
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none text-sm"
                      value={searchTerm}
                      onChange={e => setSearchTerm(e.target.value)}
                    />
                    {searchTerm && (
                      <button onClick={() => setSearchTerm('')} className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600">
                        <X size={16} />
                      </button>
                    )}
                  </div>

                  {/* Age Range */}
                  <div className="flex items-center gap-2">
                    <div className="relative w-24">
                      <input
                        type="number"
                        placeholder="Min"
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none text-sm"
                        value={ageRange.min}
                        onChange={e => setAgeRange({ ...ageRange, min: e.target.value })}
                      />
                    </div>
                    <span className="text-gray-400">-</span>
                    <div className="relative w-24">
                      <input
                        type="number"
                        placeholder="Max"
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none text-sm"
                        value={ageRange.max}
                        onChange={e => setAgeRange({ ...ageRange, max: e.target.value })}
                      />
                    </div>
                    <button
                      onClick={() => setAgeRange({ min: '', max: '' })}
                      className="p-2 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400"
                      title="清除篩選"
                    >
                      <Filter size={18} />
                    </button>
                  </div>
                </div>

                <div className="flex justify-between items-center text-xs text-gray-500 dark:text-gray-400 px-1">
                  <span>顯示 {processedUsers.length} / {users.length} 筆資料</span>
                  {isDemoMode && <span className="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-0.5 rounded">Demo Mode</span>}
                </div>
              </div>

              {/* Table Header */}
              <div className="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600 grid grid-cols-12 gap-4 p-4 text-xs font-semibold text-gray-500 dark:text-gray-300 uppercase tracking-wider sticky top-0 z-10">
                <div
                  className="col-span-6 flex items-center gap-2 cursor-pointer hover:text-blue-600 dark:hover:text-blue-400 select-none"
                  onClick={() => handleSort('name')}
                >
                  NAME <SortIcon columnKey="name" />
                </div>
                <div
                  className="col-span-4 flex items-center gap-2 cursor-pointer hover:text-blue-600 dark:hover:text-blue-400 select-none"
                  onClick={() => handleSort('age')}
                >
                  AGE <SortIcon columnKey="age" />
                </div>
                <div className="col-span-2 text-right">ACTION</div>
              </div>

              {/* User List Body */}
              <div className="overflow-y-auto flex-1 p-0 custom-scrollbar">
                {processedUsers.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-64 text-gray-400 space-y-2">
                    <Search size={48} className="opacity-20" />
                    <p>沒有符合條件的使用者</p>
                  </div>
                ) : (
                  <div className="divide-y divide-gray-100 dark:divide-gray-700">
                    {processedUsers.map((user, idx) => (
                      <div key={`${user.name}-${idx}`} className="grid grid-cols-12 gap-4 p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors group items-center">
                        <div className="col-span-6 font-medium text-gray-900 dark:text-gray-100 truncate">{user.name}</div>
                        <div className="col-span-4 text-gray-600 dark:text-gray-400">{user.age}</div>
                        <div className="col-span-2 text-right">
                          <button
                            onClick={() => handleDeleteUser(user.name)}
                            className="text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors p-1.5 rounded hover:bg-red-50 dark:hover:bg-red-900/20"
                            title="刪除"
                          >
                            <Trash2 size={18} />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default App;