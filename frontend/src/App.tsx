import { useState, useMemo, useEffect } from 'react';
import { 
  AlertCircle, 
  CheckCircle2, 
  Clock, 
  ShieldAlert, 
  Search,
  LayoutDashboard,
  Activity,
  UserPlus,
  AlertTriangle,
  RefreshCcw,
  Calendar,
  Hash,
  User,
  HelpCircle,
  Users,
  LogOut,
  Mail,
  BadgeCheck,
  Info,
  ExternalLink,
  Menu,
  X,
  Tag,
  FileSpreadsheet,
  UploadCloud,
  Download,
  Trash2,
  Sparkles
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { Incident, Priority, Status, TeamMember, Category, BatchFile } from './types';

type View = 'dashboard' | 'profile' | 'help' | 'team' | 'batch';

const StatusBadge = ({ status }: { status: Status }) => {
  const styles = {
    Open: 'bg-red-50 text-red-700 border-red-200',
    Assigned: 'bg-blue-50 text-blue-700 border-blue-200',
    Resolved: 'bg-green-50 text-green-700 border-green-200',
    Classified: 'bg-yellow-50 text-yellow-700 border-yellow-200',
  };

  const icons = {
    Open: <AlertCircle className="w-3.5 h-3.5" />,
    Assigned: <Clock className="w-3.5 h-3.5" />,
    Resolved: <CheckCircle2 className="w-3.5 h-3.5" />,
    Classified: <ShieldAlert className="w-3.5 h-3.5" />,
  };

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border shadow-sm ${styles[status]}`}>
      {icons[status]}
      {status}
    </span>
  );
};

const PriorityBadge = ({ priority }: { priority: Priority }) => {
  let style = 'bg-slate-100 text-slate-600 border-slate-200';
  if (typeof priority === 'string') {
    const p = priority.toLowerCase();
    if (p.includes('critical')) style = 'bg-red-50 text-red-600 border-red-200 font-bold';
    else if (p.includes('high')) style = 'bg-orange-50 text-orange-600 border-orange-200';
    else if (p.includes('medium')) style = 'bg-blue-50 text-blue-600 border-blue-200';
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] uppercase tracking-wider border font-bold ${style}`}>
      {priority}
    </span>
  );
};

interface IncidentCardProps {
  key?: string | number;
  incident: Incident;
  onClassifyClick: (incident: Incident) => void;
  onAssignClick: (incident: Incident) => void;
  onResolveClick: (incident: Incident) => void;
}

const IncidentCard = ({ incident, onClassifyClick, onAssignClick, onResolveClick }: IncidentCardProps) => {
  return (
    <motion.div 
      layout
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-all group flex flex-col h-full"
    >
      <div className="p-5 flex-grow">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="bg-slate-100 p-1.5 rounded-lg">
              <Hash className="w-4 h-4 text-slate-500" />
            </div>
            <span className="text-sm font-bold text-slate-900">{incident.id}</span>
          </div>
          <PriorityBadge priority={incident.priority} />
        </div>
        
        <h3 className="text-slate-800 font-semibold text-sm mb-4 leading-relaxed line-clamp-3 group-hover:line-clamp-none transition-all">
          {incident.description}
        </h3>

        <div className="flex flex-wrap gap-3 items-center mt-auto">
          <StatusBadge status={incident.status} />
          {incident.category && incident.category !== "Unassigned" && (
            <div className="flex items-center gap-1.5 text-xs text-yellow-700 font-bold bg-yellow-50 px-2 py-1 rounded-md border border-yellow-100">
              <Tag className="w-3.5 h-3.5" />
              {incident.category}{incident.subcategory && incident.subcategory !== "Unassigned" ? ` / ${incident.subcategory}` : ''}
            </div>
          )}
          <div className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
            <Calendar className="w-3.5 h-3.5" />
            {new Date(incident.createdAt).toLocaleDateString()}
          </div>
          {incident.assignedTo && incident.assignedTo !== "Unassigned" && (
            <div className="flex items-center gap-1.5 text-xs text-indigo-600 font-bold bg-indigo-50 px-2 py-1 rounded-md">
              <User className="w-3.5 h-3.5" />
              {incident.assignedTo}
            </div>
          )}
        </div>
      </div>

      <div className="px-5 py-4 bg-slate-50/50 border-t border-slate-100 rounded-b-2xl flex items-center justify-between">
        <div className="flex items-center gap-2">
          {incident.status === 'Open' && (
            <button 
              onClick={() => onClassifyClick(incident)}
              className="px-3 py-1.5 text-xs font-bold text-yellow-700 hover:bg-yellow-100 rounded-lg transition-all flex items-center gap-1.5"
            >
              <ShieldAlert className="w-3.5 h-3.5" />
              Classify
            </button>
          )}
          {incident.status === 'Classified' && (
            <button 
              onClick={() => onAssignClick(incident)}
              className="px-3 py-1.5 text-xs font-bold text-blue-700 hover:bg-blue-100 rounded-lg transition-all flex items-center gap-1.5"
            >
              <UserPlus className="w-3.5 h-3.5" />
              Assign
            </button>
          )}
          {incident.status === 'Assigned' && (
            <button 
              onClick={() => onResolveClick(incident)}
              className="px-3 py-1.5 text-xs font-bold text-green-700 hover:bg-green-100 rounded-lg transition-all flex items-center gap-1.5"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              Resolve
            </button>
          )}
          {incident.status === 'Resolved' && (
            <span className="text-xs font-medium text-slate-400 italic px-3 py-1.5">No pending actions</span>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default function App() {
  const [currentView, setCurrentView] = useState<View>('dashboard');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<Status | 'All'>('All');
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<{id: string, message: string, timestamp: Date}[]>([]);
  const [batchFile, setBatchFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<{type: 'success' | 'error', text: string} | null>(null);
  const [batchFiles, setBatchFiles] = useState<BatchFile[]>([]);
  const [selectedFileId, setSelectedFileId] = useState<string | null>(null);
  const [columnMapping, setColumnMapping] = useState<Record<string, string>>({});
  const [selectedFileInsights, setSelectedFileInsights] = useState<any | null>(null);
  const [isInsightsLoading, setIsInsightsLoading] = useState(false);
  const [insightsTab, setInsightsTab] = useState<'visuals' | 'analyst'>('visuals');
  const [selectedFileSummary, setSelectedFileSummary] = useState<any | null>(null);
  const [isSummaryLoading, setIsSummaryLoading] = useState(false);
  const [selectedFileRecs, setSelectedFileRecs] = useState<any[] | null>(null);
  const [isRecsLoading, setIsRecsLoading] = useState(false);
  const [questionText, setQuestionText] = useState('');
  const [answerText, setAnswerText] = useState('');
  const [isAsking, setIsAsking] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [selectedTrendDate, setSelectedTrendDate] = useState<string | null>(null);
  const [spikeWindowFilter, setSpikeWindowFilter] = useState<'7D' | '30D'>('7D');
  const [isLlmEnabled, setIsLlmEnabled] = useState(true);

  const fetchIncidents = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/incidents');
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Failed to connect to the incident management server.');
      }
      
      const rawData = await response.json();
      
      const mappedData: Incident[] = rawData.map((item: any) => ({
        id: item.id,
        description: item.description,
        priority: item.priority || 'Medium',
        status: item.status,
        category: item.category,
        subcategory: item.subcategory,
        assignedTo: item.assigned_to || item.assignment_group,
        createdAt: new Date().toISOString(),
      }));

      setIncidents(mappedData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred.');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchTeam = async () => {
    try {
      const res = await fetch('/api/team');
      if (res.ok) {
        setTeamMembers(await res.json());
      }
    } catch (err) {
      console.error("Failed to load team", err);
    }
  };

  const fetchBatchFiles = async () => {
    try {
      const res = await fetch('/api/batch/files');
      if (res.ok) {
        setBatchFiles(await res.json());
      }
    } catch (err) {
      console.error("Failed to load batch files", err);
    }
  };

  const fetchInsights = async (fileId: string, start?: string, end?: string) => {
    setIsInsightsLoading(true);
    try {
      let url = `/api/insights?file_id=${fileId}`;
      if (start) url += `&start_date=${start}`;
      if (end) url += `&end_date=${end}`;
      const res = await fetch(url);
      if (res.ok) {
        setSelectedFileInsights(await res.json());
      } else {
        setSelectedFileInsights(null);
      }
    } catch (err) {
      console.error("Failed to load insights", err);
      setSelectedFileInsights(null);
    } finally {
      setIsInsightsLoading(false);
    }
  };

  const fetchSummary = async (fileId: string, start?: string, end?: string) => {
    setIsSummaryLoading(true);
    try {
      let url = `/api/summary?file_id=${fileId}&force_llm=${isLlmEnabled}`;
      if (start) url += `&start_date=${start}`;
      if (end) url += `&end_date=${end}`;
      const res = await fetch(url);
      if (res.ok) {
        setSelectedFileSummary(await res.json());
      } else {
        setSelectedFileSummary(null);
      }
    } catch (err) {
      console.error("Failed to load summary", err);
      setSelectedFileSummary(null);
    } finally {
      setIsSummaryLoading(false);
    }
  };

  const fetchRecommendations = async (fileId: string, start?: string, end?: string) => {
    setIsRecsLoading(true);
    try {
      let url = `/api/recommendations?file_id=${fileId}&force_llm=${isLlmEnabled}`;
      if (start) url += `&start_date=${start}`;
      if (end) url += `&end_date=${end}`;
      const res = await fetch(url);
      if (res.ok) {
        setSelectedFileRecs(await res.json());
      } else {
        setSelectedFileRecs(null);
      }
    } catch (err) {
      console.error("Failed to load recommendations", err);
      setSelectedFileRecs(null);
    } finally {
      setIsRecsLoading(false);
    }
  };

  const handleAskQuestion = async () => {
    if (!questionText.trim() || !selectedFileId) return;
    setIsAsking(true);
    setAnswerText('');
    try {
      const res = await fetch(`/api/ask?force_llm=${isLlmEnabled}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: questionText, file_id: selectedFileId })
      });
      if (res.ok) {
        const result = await res.json();
        setAnswerText(result.answer || 'No answer received.');
      } else {
        setAnswerText('Failed to fetch answer from AI Assistant.');
      }
    } catch (err) {
      console.error("Failed to ask question", err);
      setAnswerText('An error occurred while communicating with the AI Assistant.');
    } finally {
      setIsAsking(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
    fetchTeam();
    fetchBatchFiles();
  }, []);

  useEffect(() => {
    if (selectedFileId) {
      const file = batchFiles.find(f => f.id === selectedFileId);
      if (file && file.status === 'Classified') {
        fetchInsights(selectedFileId, startDate, endDate);
        fetchSummary(selectedFileId, startDate, endDate);
        fetchRecommendations(selectedFileId, startDate, endDate);
        setAnswerText('');
        setQuestionText('');
      } else {
        setSelectedFileInsights(null);
        setSelectedFileSummary(null);
        setSelectedFileRecs(null);
        setAnswerText('');
        setQuestionText('');
      }
    } else {
      setSelectedFileInsights(null);
      setSelectedFileSummary(null);
      setSelectedFileRecs(null);
      setAnswerText('');
      setQuestionText('');
    }
  }, [selectedFileId, batchFiles, startDate, endDate, isLlmEnabled]);

  const addToHistory = (message: string) => {
    setHistory(prev => [{
      id: Math.random().toString(36).substring(2, 9),
      message,
      timestamp: new Date()
    }, ...prev].slice(0, 50));
  };
  
  // API Flow Actions
  const handleClassify = async (incident: Incident) => {
    addToHistory(`Classifying ${incident.id}`);
    try {
       const res = await fetch(`/api/incidents/${incident.id}/classify`, {method: 'POST'});
       if(res.ok) {
           const result = await res.json();
           setIncidents(prev => prev.map(i => i.id === incident.id ? {
               ...i,
               status: 'Classified',
               category: result.category,
               subcategory: result.subcategory,
               priority: result.priority
           } : i));
           addToHistory(`${incident.id} classified as ${result.category}/${result.subcategory}`);
       } else throw new Error("API responded with an error");
    } catch(err) {
       console.error(err);
       addToHistory(`Classification failed for ${incident.id}.`);
    }
  };

  const handleAssign = async (incident: Incident) => {
    addToHistory(`Determining best assignment for ${incident.id}...`);
    try {
       const res = await fetch(`/api/incidents/${incident.id}/assign`, {method: 'POST'});
       if(res.ok) {
           const result = await res.json();
           setIncidents(prev => prev.map(i => i.id === incident.id ? {
               ...i,
               status: 'Assigned',
               assignedTo: result.assigned_to !== 'Unknown' && result.assigned_to ? result.assigned_to : result.assignment_group
           } : i));
           addToHistory(`${incident.id} assigned to ${result.assignment_group} / ${result.assigned_to}`);
       } else throw new Error("API responded with an error");
    } catch(err) {
       console.error(err);
       addToHistory(`Assignment failed for ${incident.id}.`);
    }
  };

  const handleResolve = async (incident: Incident) => {
    addToHistory(`Marking ${incident.id} as resolved...`);
    try {
       const res = await fetch(`/api/incidents/${incident.id}/resolve`, {method: 'POST'});
       if(res.ok) {
           setIncidents(prev => prev.map(i => i.id === incident.id ? {
               ...i,
               status: 'Resolved'
           } : i));
           addToHistory(`${incident.id} successfully resolved.`);
       } else throw new Error("API responded with an error");
    } catch(err) {
       console.error(err);
       addToHistory(`Failed to resolve ${incident.id}.`);
    }
  };

  const handleBatchUpload = async () => {
    if (!batchFile) return;
    
    setIsUploading(true);
    setUploadMessage(null);
    
    const formData = new FormData();
    formData.append('file', batchFile);
    
    try {
      const res = await fetch('/api/batch/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (res.ok) {
        const newFile = await res.json();
        setBatchFiles(prev => [newFile, ...prev]);
        setUploadMessage({type: 'success', text: 'File uploaded successfully!'});
        setBatchFile(null);
        setSelectedFileId(newFile.id);
      } else {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.error || 'Failed to upload file');
      }
    } catch (err) {
      setUploadMessage({type: 'error', text: err instanceof Error ? err.message : 'An unknown error occurred'});
    } finally {
      setIsUploading(false);
    }
  };

  const handleProcessBatch = async (fileId: string) => {
    setIsUploading(true);
    try {
      const res = await fetch(`/api/batch/files/${fileId}/process`, { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mapping: columnMapping })
      });
      if (res.ok) {
        setBatchFiles(prev => prev.map(f => f.id === fileId ? { ...f, status: 'Classified', column_mapping: columnMapping } : f));
        addToHistory(`Batch file ${fileId} processed successfully`);
      } else {
        throw new Error("Failed to process batch file");
      }
    } catch (err) {
      console.error(err);
      addToHistory(`Batch processing failed for ${fileId}`);
    } finally {
      setIsUploading(false);
    }
  };



  const handleDownloadBatch = async (fileId: string, filename: string) => {
    try {
      const res = await fetch(`/api/batch/files/${fileId}/download`);
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `processed_${filename.replace(/\.[^/.]+$/, "")}.xlsx`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteFile = async (fileId: string) => {
    if (!window.confirm("Are you sure you want to delete this batch file?")) return;
    try {
      const res = await fetch(`/api/batch/files/${fileId}`, { method: 'DELETE' });
      if (res.ok) {
        setBatchFiles(prev => prev.filter(f => f.id !== fileId));
        setSelectedFileId(null);
        addToHistory(`Batch file deleted`);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const filteredIncidents = useMemo(() => {
    return incidents.filter(incident => {
      const matchesSearch = incident.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            incident.id.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = statusFilter === 'All' || incident.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [searchTerm, statusFilter, incidents]);

  let stats = useMemo(() => {
    return {
      total: incidents.length,
      open: incidents.filter(i => i.status === 'Open').length,
      resolved: incidents.filter(i => i.status === 'Resolved').length,
      critical: incidents.filter(i => String(i.priority).toLowerCase().includes('critical')).length,
    };
  }, [incidents]);

  const sidebarItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'team', label: 'Team Directory', icon: Users },
    { id: 'batch', label: 'Batch Processing', icon: FileSpreadsheet },
    { id: 'profile', label: 'My Profile', icon: User },
    { id: 'help', label: 'Help Center', icon: HelpCircle },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans flex overflow-hidden">
      {/* Sidebar */}
      <aside 
        className={`bg-white border-r border-slate-200 flex flex-col transition-all duration-300 z-30 fixed lg:static h-full ${
          isSidebarOpen ? 'w-64 translate-x-0' : 'w-20 -translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="p-6 flex items-center gap-3 border-b border-slate-100">
          <div className="bg-indigo-600 p-2 rounded-xl shadow-lg shadow-indigo-200 shrink-0">
            <Activity className="text-white w-5 h-5" />
          </div>
          {isSidebarOpen && (
            <div className="overflow-hidden whitespace-nowrap">
              <h1 className="text-lg font-bold tracking-tight text-slate-900 leading-none mb-1">IncidentControl</h1>
              <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Ops Dashboard</p>
            </div>
          )}
        </div>

        <nav className="flex-grow p-4 space-y-2">
          {sidebarItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setCurrentView(item.id as View)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-bold text-sm ${
                currentView === item.id 
                ? 'bg-indigo-50 text-indigo-600 shadow-sm' 
                : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
              }`}
            >
              <item.icon className="w-5 h-5 shrink-0" />
              {isSidebarOpen && <span>{item.label}</span>}
            </button>
          ))}
        </nav>

      </aside>

      {/* Main Content Area */}
      <div className="flex-grow flex flex-col h-screen overflow-hidden">
        {/* Top Header */}
        <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between z-20">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 hover:bg-slate-100 rounded-lg lg:hidden"
            >
              {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <h2 className="text-lg font-bold text-slate-900 capitalize">{currentView}</h2>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-xl hover:bg-slate-100 transition-colors cursor-pointer" onClick={() => setIsLlmEnabled(!isLlmEnabled)}>
              <Sparkles className={`w-3.5 h-3.5 ${isLlmEnabled ? 'text-indigo-600' : 'text-slate-400'}`} />
              <span className="text-[10px] font-black text-slate-500 uppercase tracking-wide">AI Engine</span>
              <div className={`w-7 h-4 rounded-full relative transition-colors ${isLlmEnabled ? 'bg-indigo-600' : 'bg-slate-300'}`}>
                <div className={`w-2.5 h-2.5 bg-white rounded-full absolute top-0.75 transition-all ${isLlmEnabled ? 'right-0.75' : 'left-0.75'}`} />
              </div>
            </div>
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-green-50 border border-green-100 rounded-full text-[10px] font-bold text-green-700 uppercase tracking-wider">
              <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
              All Systems Nominal
            </div>
            <button 
              onClick={() => setCurrentView('profile')}
              className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-bold text-white shadow-lg shadow-indigo-200 hover:scale-110 transition-transform cursor-pointer"
              title="View Profile"
            >
              KK
            </button>
          </div>
        </header>

        {/* Content Scroll Area */}
        <div className="flex-grow overflow-y-auto p-6 lg:p-8">
          <AnimatePresence mode="wait">
            {currentView === 'dashboard' && (
              <motion.div
                key="dashboard"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
              >
                {isLoading ? (
                  <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
                    <div className="relative">
                      <div className="w-16 h-16 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin"></div>
                      <Activity className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-6 h-6 text-indigo-600" />
                    </div>
                    <h3 className="text-lg font-bold text-slate-900">Synchronizing Data...</h3>
                  </div>
                ) : error ? (
                  <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6 text-center">
                    <AlertTriangle className="w-16 h-16 text-red-500" />
                    <h3 className="text-xl font-bold text-slate-900">Connection Interrupted</h3>
                    <p className="text-slate-500 max-w-md">{error}</p>
                    <button onClick={fetchIncidents} className="px-8 py-3 bg-indigo-600 text-white rounded-2xl font-bold shadow-xl shadow-indigo-500/30">Retry</button>
                  </div>
                ) : (
                  <>
                    {/* Stats Grid */}
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                      {[
                        { label: 'Total Incidents', value: stats.total, icon: LayoutDashboard, color: 'text-indigo-600', bg: 'bg-indigo-50' },
                        { label: 'Open Tickets', value: stats.open, icon: AlertCircle, color: 'text-red-600', bg: 'bg-red-50' },
                        { label: 'Resolved Today', value: stats.resolved, icon: CheckCircle2, color: 'text-green-600', bg: 'bg-green-50' },
                        { label: 'Critical Issues', value: stats.critical, icon: ShieldAlert, color: 'text-orange-600', bg: 'bg-orange-50' },
                      ].map((stat, idx) => (
                        <div key={stat.label} className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
                          <div className="flex items-center justify-between mb-4">
                            <div className={`${stat.bg} p-2 rounded-xl`}><stat.icon className={`w-5 h-5 ${stat.color}`} /></div>
                            <span className="text-[10px] font-black text-slate-300 uppercase tracking-widest">Realtime</span>
                          </div>
                          <div className="text-3xl font-black text-slate-900 mb-1">{stat.value}</div>
                          <div className="text-xs text-slate-500 font-bold uppercase tracking-wider">{stat.label}</div>
                        </div>
                      ))}
                    </div>

                    {/* Toolbar */}
                    <div className="flex flex-col lg:flex-row gap-4 items-center justify-between mb-8">
                      <div className="relative w-full lg:w-1/2">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                        <input 
                          type="text"
                          placeholder="Search incidents..."
                          className="w-full pl-12 pr-6 py-4 bg-white border border-slate-200 rounded-2xl text-sm font-medium focus:outline-none focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all shadow-sm"
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                        />
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <button
                          onClick={fetchIncidents}
                          className="px-4 py-2.5 rounded-xl text-xs font-bold transition-all border bg-slate-900 text-white hover:bg-slate-800"
                        >
                          <RefreshCcw className="w-4 h-4 inline mr-1" />
                          Refresh Incidents
                        </button>
                        {['All', 'Open', 'Assigned', 'Resolved', 'Classified'].map((status) => (
                          <button
                            key={status}
                            onClick={() => setStatusFilter(status as Status | 'All')}
                            className={`px-4 py-2.5 rounded-xl text-xs font-bold transition-all border ${
                              statusFilter === status 
                              ? 'bg-indigo-600 text-white border-indigo-600 shadow-lg shadow-indigo-200' 
                              : 'bg-white text-slate-600 border-slate-200 hover:border-indigo-300'
                            }`}
                          >
                            {status}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Incident Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 xlg:grid-cols-3 gap-6 mb-12">
                      <AnimatePresence mode="popLayout">
                        {filteredIncidents.map((incident) => (
                          <IncidentCard 
                            key={incident.id} 
                            incident={incident} 
                            onClassifyClick={handleClassify}
                            onAssignClick={handleAssign}
                            onResolveClick={handleResolve}
                          />
                        ))}
                      </AnimatePresence>
                    </div>

                    {/* History Panel */}
                    <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden mb-8">
                      <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
                        <div className="flex items-center gap-2">
                          <Activity className="w-4 h-4 text-indigo-600" />
                          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Recent Activity Log</h3>
                        </div>
                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Live Updates</span>
                      </div>
                      <div className="max-h-48 overflow-y-auto divide-y divide-slate-50">
                        {history.length > 0 ? (
                          history.map((log) => (
                            <div key={log.id} className="px-6 py-3 flex items-center justify-between hover:bg-slate-50/50 transition-colors">
                              <div className="flex items-center gap-3">
                                <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full"></div>
                                <span className="text-sm text-slate-700 font-medium">{log.message}</span>
                              </div>
                              <span className="text-[10px] text-slate-400 font-bold">
                                {log.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                              </span>
                            </div>
                          ))
                        ) : (
                          <div className="px-6 py-8 text-center text-slate-400 italic text-sm">
                            No recent activity recorded.
                          </div>
                        )}
                      </div>
                    </div>
                  </>
                )}
              </motion.div>
            )}

            {currentView === 'batch' && (
              <motion.div
                key="batch"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="grid grid-cols-1 xl:grid-cols-12 gap-8"
              >
                {/* Left Column: File List */}
                <div className="xl:col-span-8 space-y-6">
                  <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
                      <div className="px-8 py-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
                        <div className="flex items-center gap-3">
                          <div className="bg-indigo-600 p-2 rounded-xl">
                            <FileSpreadsheet className="w-5 h-5 text-white" />
                          </div>
                          <div>
                            <h3 className="text-lg font-bold text-slate-900">Batch Repository</h3>
                            <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Classification Engine v2.1</p>
                          </div>
                        </div>
                        <div className="flex flex-col items-end">
                          <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{batchFiles.length} Files Total</span>
                          <span className="text-[10px] text-indigo-600 font-black uppercase tracking-widest">Performance: ~100 rows/sec</span>
                        </div>
                      </div>
                    
                    <div className="overflow-x-auto">
                      <table className="w-full text-left">
                        <thead>
                          <tr className="border-b border-slate-50 text-[10px] font-black text-slate-400 uppercase tracking-widest">
                            <th className="px-8 py-4">File Name</th>
                            <th className="px-8 py-4">Uploaded On</th>
                            <th className="px-8 py-4 text-center">Status</th>

                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50">
                          {batchFiles.length > 0 ? (
                            batchFiles.map((file) => (
                              <tr 
                                key={file.id} 
                                onClick={() => {
                                  setSelectedFileId(file.id);
                                  setColumnMapping(file.column_mapping || {});
                                }}
                                className={`group cursor-pointer transition-all ${selectedFileId === file.id ? 'bg-indigo-50/50' : 'hover:bg-slate-50/50'}`}
                              >
                                <td className="px-8 py-5">
                                  <div className="flex items-center gap-3">
                                    <div className={`p-2 rounded-lg ${selectedFileId === file.id ? 'bg-indigo-100 text-indigo-600' : 'bg-slate-100 text-slate-400 group-hover:bg-indigo-50 group-hover:text-indigo-500'}`}>
                                      <FileSpreadsheet className="w-4 h-4" />
                                    </div>
                                    <span className="text-sm font-bold text-slate-700">{file.filename}</span>
                                  </div>
                                </td>
                                <td className="px-8 py-5">
                                  <span className="text-xs font-medium text-slate-500">
                                    {new Date(file.uploaded_at).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}
                                  </span>
                                </td>
                                <td className="px-8 py-5">
                                  <div className="flex justify-center">
                                    <span className={`px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-wider border ${
                                      file.status === 'Classified' 
                                      ? 'bg-green-50 text-green-700 border-green-200' 
                                      : 'bg-blue-50 text-blue-700 border-blue-200'
                                    }`}>
                                      {file.status === 'Classified' ? 'Analyzed' : file.status}
                                    </span>
                                  </div>
                                </td>

                              </tr>
                            ))
                          ) : (
                            <tr>
                              <td colSpan={4} className="px-8 py-12 text-center text-slate-400 italic text-sm">
                                No files uploaded yet. Start by uploading an Excel file.
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Bigger Ticket Analysis & AI Insights Columns */}
                  {selectedFileId && (() => {
                    const file = batchFiles.find(f => f.id === selectedFileId);
                    if (!file) return null;
                    const allSpikes = selectedFileInsights ? [
                      ...(spikeWindowFilter === '7D' ? (selectedFileInsights.spikes_7d || []) : []),
                      ...(spikeWindowFilter === '30D' ? (selectedFileInsights.spikes_30d || []) : [])
                    ] : [];
                    return (
                      <div className="space-y-6">

                        {/* Real-time AI Insights Panel */}
                        {file.status === 'Classified' && (
                          <motion.div 
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-white rounded-3xl border border-slate-200 shadow-sm p-8"
                          >
                            <div className="flex flex-col gap-5 mb-8 border-b border-slate-100 pb-5">
                              {/* Row 1: Title & Date Range */}
                              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                                <div className="flex items-center gap-3">
                                  <div className="bg-indigo-600 p-2.5 rounded-xl shadow-lg shadow-indigo-100 text-white flex items-center justify-center">
                                    <Activity className="w-5 h-5" />
                                  </div>
                                  <div>
                                    <h3 className="text-lg font-bold text-slate-900">AI Dataset Insights</h3>
                                    <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Real-Time Dataset Analytics</p>
                                  </div>
                                </div>
                                
                                <div className="flex flex-wrap items-center gap-4 bg-slate-50 border border-slate-200/50 p-2 rounded-2xl shrink-0">
                                  <div className="flex items-center gap-1.5">
                                    <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest pl-1.5">Start</span>
                                    <input 
                                      type="date" 
                                      className="bg-white border border-slate-200 rounded-lg px-2.5 py-1 text-[11px] font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500/10 text-slate-700 cursor-pointer"
                                      value={startDate}
                                      onChange={(e) => setStartDate(e.target.value)}
                                    />
                                  </div>
                                  <div className="flex items-center gap-1.5">
                                    <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">End</span>
                                    <input 
                                      type="date" 
                                      className="bg-white border border-slate-200 rounded-lg px-2.5 py-1 text-[11px] font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500/10 text-slate-700 cursor-pointer"
                                      value={endDate}
                                      onChange={(e) => setEndDate(e.target.value)}
                                    />
                                  </div>
                                  {(startDate || endDate) && (
                                    <button 
                                      onClick={() => { setStartDate(''); setEndDate(''); }}
                                      className="px-2 py-1 bg-white hover:bg-slate-100 border border-slate-200 rounded-lg text-[9px] font-black uppercase text-slate-500 transition-all cursor-pointer"
                                      title="Clear Dates"
                                    >
                                      Reset
                                    </button>
                                  )}
                                </div>
                              </div>
                              
                              {/* Row 2: Tab Toggle switch below */}
                              <div className="flex justify-start">
                                <div className="flex items-center bg-slate-100 p-1 rounded-xl shrink-0">
                                  <button
                                    onClick={() => setInsightsTab('visuals')}
                                    className={`px-4 py-2 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                                      insightsTab === 'visuals' 
                                        ? 'bg-white text-indigo-600 shadow-sm' 
                                        : 'text-slate-500 hover:text-slate-900'
                                    }`}
                                  >
                                    Visual Charts
                                  </button>
                                  <button
                                    onClick={() => setInsightsTab('analyst')}
                                    className={`px-4 py-2 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                                      insightsTab === 'analyst' 
                                        ? 'bg-white text-indigo-600 shadow-sm' 
                                        : 'text-slate-500 hover:text-slate-900'
                                    }`}
                                  >
                                    AI Analyst
                                  </button>
                                </div>
                              </div>
                            </div>

                            {insightsTab === 'visuals' ? (
                              selectedFileInsights ? (
                                <div className="space-y-8">
                                  {/* Summary Metrics Grid */}
                                  <div className="grid grid-cols-1 gap-6">
                                    <div className="bg-slate-50/50 rounded-2xl border border-slate-100 p-5 flex items-center justify-between">
                                      <div>
                                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest block mb-1">Total Incidents</span>
                                        <span className="text-3xl font-black text-slate-900">{selectedFileInsights.total_tickets}</span>
                                        <span className="text-xs text-slate-500 font-bold block mt-1">Records Processed</span>
                                      </div>
                                      <div className="bg-indigo-50 p-3 rounded-xl text-indigo-600">
                                        <CheckCircle2 className="w-6 h-6" />
                                      </div>
                                    </div>
                                  </div>

                                  {/* Daily Incident Surges & Trends Sparkline */}
                                  {selectedFileInsights && selectedFileInsights.trends && selectedFileInsights.trends.length > 0 && (
                                    <div className="bg-slate-50/50 border border-slate-100 rounded-3xl p-6 space-y-4">
                                      <div className="flex items-center justify-between mb-2 flex-wrap gap-3">
                                        <div className="flex items-center gap-4">
                                          <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">Daily Incident Surges & Trends</span>
                                          <div className="bg-slate-100 p-0.5 rounded-lg flex items-center">
                                            {['7D', '30D'].map((opt) => (
                                              <button
                                                key={opt}
                                                onClick={() => setSpikeWindowFilter(opt as any)}
                                                className={`px-2 py-0.5 text-[8px] font-black rounded-md uppercase transition-all ${
                                                  spikeWindowFilter === opt 
                                                    ? 'bg-white text-indigo-600 shadow-sm' 
                                                    : 'text-slate-400 hover:text-slate-600'
                                                }`}
                                              >
                                                {opt}
                                              </button>
                                            ))}
                                          </div>
                                        </div>
                                        
                                        {allSpikes.length > 0 && (
                                          <span className="bg-red-50 text-red-600 px-2.5 py-1 rounded-full text-[8px] font-extrabold uppercase animate-pulse border border-red-100">
                                            {allSpikes.length} Surges Flagged
                                          </span>
                                        )}
                                      </div>
                                      <div className="w-full overflow-x-auto pb-1">
                                        <div className="h-36 flex items-end gap-2.5 pt-12">
                                          {selectedFileInsights.trends.map((t: any, idx: number) => {
                                            const maxCount = Math.max(...selectedFileInsights.trends.map((tr: any) => tr.count), 1);
                                            const heightPct = (t.count / maxCount) * 100;
                                            const isSpike = allSpikes.some((s: any) => s.date === t.date);
                                            return (
                                              <div 
                                                key={idx} 
                                                onClick={() => setSelectedTrendDate(selectedTrendDate === t.date ? null : t.date)}
                                                className="w-8 shrink-0 flex flex-col items-center gap-1.5 h-full justify-end group relative animate-fadeIn cursor-pointer"
                                              >
                                                <div className="absolute -top-8 scale-0 group-hover:scale-100 bg-slate-900 text-white text-[9px] px-2 py-1 rounded-md transition-all font-black shadow-lg pointer-events-none z-20 whitespace-nowrap left-1/2 -translate-x-1/2">
                                                  {t.date}: {t.count} tickets
                                                </div>
                                                <div 
                                                  className={`w-full rounded-t-md transition-all duration-300 cursor-pointer ${
                                                    selectedTrendDate === t.date 
                                                      ? 'bg-amber-400 scale-x-110 shadow-lg shadow-amber-200/50' 
                                                      : isSpike 
                                                        ? 'bg-red-500 hover:bg-red-600' 
                                                        : 'bg-indigo-600 hover:bg-indigo-700'
                                                  }`} 
                                                  style={{ height: `${heightPct || 4}%` }}
                                                ></div>
                                                <span className="text-[8px] text-slate-400 font-bold tracking-tight mt-1 truncate w-8 text-center">{t.date.split('-')[2] || t.date}</span>
                                              </div>
                                            );
                                          })}
                                        </div>
                                      </div>

                                      {/* Trend Date Detail Panel */}
                                      {selectedTrendDate && (() => {
                                        const trendObj = selectedFileInsights.trends.find((tr: any) => tr.date === selectedTrendDate);
                                        if (!trendObj) return null;
                                        const isSpike = allSpikes.some((s: any) => s.date === selectedTrendDate);
                                        const spikeDetails = isSpike ? allSpikes.find((s: any) => s.date === selectedTrendDate) : null;
                                        
                                        return (
                                          <motion.div 
                                            initial={{ opacity: 0, height: 0 }}
                                            animate={{ opacity: 1, height: 'auto' }}
                                            className="bg-slate-50 border border-slate-200/60 rounded-2xl p-5 mt-4 space-y-3"
                                          >
                                            <div className="flex items-center justify-between">
                                              <div>
                                                <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest block mb-1">Selected Analysis Date</span>
                                                <span className="text-xs font-bold text-slate-800">
                                                  {new Date(selectedTrendDate).toLocaleDateString([], { dateStyle: 'long' })}
                                                </span>
                                              </div>
                                              <div>
                                                {isSpike ? (
                                                  <span className="bg-red-50 text-red-600 border border-red-200 px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-wider block animate-pulse">
                                                    Surge Detected
                                                  </span>
                                                ) : (
                                                  <span className="bg-green-50 text-green-700 border border-green-200 px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-wider block">
                                                    Normal Activity
                                                  </span>
                                                )}
                                              </div>
                                            </div>

                                            <div className="grid grid-cols-2 gap-4 pt-2 border-t border-slate-200/40">
                                              <div>
                                                <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest block mb-1">Daily Ticket Count</span>
                                                <span className="text-lg font-extrabold text-slate-800">{trendObj.count} Tickets</span>
                                              </div>
                                              <div>
                                                <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest block mb-1">Volume Threshold</span>
                                                <span className="text-xs font-bold text-slate-600 block pt-1">
                                                  {isSpike && spikeDetails 
                                                    ? `${spikeDetails.percentage_above_avg}% Above ${spikeDetails.rolling_window_days}-Day Average` 
                                                    : "Within Healthy Standard Limits"}
                                                </span>
                                              </div>
                                            </div>

                                            <div className="bg-white border border-slate-100 rounded-xl p-3.5 mt-2">
                                              <span className="text-[9px] font-black text-indigo-600 uppercase tracking-widest block mb-1">AIOps Surge Analysis</span>
                                              <p className="text-xs text-slate-600 font-medium leading-relaxed">
                                                {isSpike 
                                                  ? `Daily ticket count of ${trendObj.count} has significantly breached the rolling threshold. This indicates a high probability of a systemic service outage or infrastructure failure. We recommend correlating this timestamp with critical service change logs.` 
                                                  : `Incident generation volume of ${trendObj.count} tickets on this day is aligned with standard operational baselines. No systemic anomaly detected.`}
                                              </p>
                                            </div>
                                          </motion.div>
                                        );
                                      })()}
                                    </div>
                                  )}

                                  {/* Distributions Breakdown Grid */}
                                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pt-4 border-t border-slate-100">
                                    {/* Top Categories */}
                                    <div className="space-y-4">
                                      <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
                                        <Tag className="w-3.5 h-3.5 text-indigo-500" />
                                        Top Categories
                                      </h4>
                                      <div className="space-y-3">
                                        {Object.entries(selectedFileInsights.categories || {}).length > 0 ? (
                                          Object.entries(selectedFileInsights.categories).slice(0, 5).map(([cat, count]: [string, any]) => {
                                            const pct = selectedFileInsights.total_tickets > 0 
                                              ? (count / selectedFileInsights.total_tickets) * 100 
                                              : 0;
                                            return (
                                              <div key={cat} className="space-y-1">
                                                <div className="flex justify-between text-xs font-bold text-slate-700">
                                                  <span>{cat}</span>
                                                  <span className="text-slate-400">{count} ({pct.toFixed(0)}%)</span>
                                                </div>
                                                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                                                  <div className="bg-indigo-600 h-full rounded-full" style={{ width: `${pct}%` }}></div>
                                                </div>
                                              </div>
                                            );
                                          })
                                        ) : (
                                          <p className="text-xs text-slate-400 italic">No category data available</p>
                                        )}
                                      </div>
                                    </div>

                                    {/* Assignment Groups */}
                                    <div className="space-y-4">
                                      <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
                                        <Users className="w-3.5 h-3.5 text-yellow-500" />
                                        Assignment Routing
                                      </h4>
                                      <div className="space-y-3">
                                        {Object.entries(selectedFileInsights.assignment_groups || {}).length > 0 ? (
                                          Object.entries(selectedFileInsights.assignment_groups).slice(0, 5).map(([grp, count]: [string, any]) => {
                                            const pct = selectedFileInsights.total_tickets > 0 
                                              ? (count / selectedFileInsights.total_tickets) * 100 
                                              : 0;
                                            return (
                                              <div key={grp} className="space-y-1">
                                                <div className="flex justify-between text-xs font-bold text-slate-700">
                                                  <span>{grp}</span>
                                                  <span className="text-slate-400">{count} ({pct.toFixed(0)}%)</span>
                                                </div>
                                                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                                                  <div className="bg-yellow-500 h-full rounded-full" style={{ width: `${pct}%` }}></div>
                                                </div>
                                              </div>
                                            );
                                          })
                                        ) : (
                                          <p className="text-xs text-slate-400 italic">No routing data available</p>
                                        )}
                                      </div>
                                    </div>
                                  </div>

                                  {/* Top Subcategories */}
                                  {selectedFileInsights.subcategories && Object.keys(selectedFileInsights.subcategories).length > 0 && (
                                    <div className="pt-6 border-t border-slate-100">
                                      <div className="space-y-4">
                                        <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
                                          <Info className="w-3.5 h-3.5 text-indigo-500" />
                                          Top Subcategories
                                        </h4>
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                          {Object.entries(selectedFileInsights.subcategories).slice(0, 3).map(([sub, count]: [string, any]) => {
                                            const pct = selectedFileInsights.total_tickets > 0 
                                              ? (count / selectedFileInsights.total_tickets) * 100 
                                              : 0;
                                            return (
                                              <div key={sub} className="flex items-center justify-between text-xs font-bold text-slate-700 bg-slate-50 border border-slate-100 px-4 py-3.5 rounded-xl">
                                                <span>{sub}</span>
                                                <span className="px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded-md text-[10px] font-bold">{count} ({pct.toFixed(0)}%)</span>
                                              </div>
                                            );
                                          })}
                                        </div>
                                      </div>
                                    </div>
                                  )}

                                    {/* Priority Distribution & Average Resolution Time */}
                                    {selectedFileInsights && selectedFileInsights.priority_distribution && Object.keys(selectedFileInsights.priority_distribution).length > 0 && (
                                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pt-6 border-t border-slate-100">
                                        {/* Priority Breakdown */}
                                        <div className="space-y-4">
                                          <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
                                            <AlertCircle className="w-3.5 h-3.5 text-red-500" />
                                            Priority Distribution
                                          </h4>
                                          <div className="space-y-3">
                                            {Object.entries(selectedFileInsights.priority_distribution).map(([prio, count]: [string, any]) => {
                                              const pct = selectedFileInsights.total_tickets > 0 
                                                ? (count / selectedFileInsights.total_tickets) * 100 
                                                : 0;
                                              return (
                                                <div key={prio} className="space-y-1">
                                                  <div className="flex justify-between text-xs font-bold text-slate-700">
                                                    <span>{prio}</span>
                                                    <span className="text-slate-400">{count} ({pct.toFixed(0)}%)</span>
                                                  </div>
                                                  <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                                                    <div className="bg-red-500 h-full rounded-full" style={{ width: `${pct}%` }}></div>
                                                  </div>
                                                </div>
                                              );
                                            })}
                                          </div>
                                        </div>

                                        {/* Priority vs Average Resolution Time */}
                                        <div className="space-y-4">
                                          <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
                                            <Clock className="w-3.5 h-3.5 text-blue-500" />
                                            Resolution Speed by Priority
                                          </h4>
                                          <div className="space-y-3">
                                            {selectedFileInsights.priority_vs_resolution_time && Object.keys(selectedFileInsights.priority_vs_resolution_time).length > 0 ? (
                                              Object.entries(selectedFileInsights.priority_vs_resolution_time).map(([prio, time]: [string, any]) => (
                                                <div key={prio} className="flex items-center justify-between text-xs font-bold text-slate-700 bg-slate-50 border border-slate-100 px-4 py-2.5 rounded-xl">
                                                  <span>{prio}</span>
                                                  <span className="px-2.5 py-1 bg-blue-50 text-blue-700 rounded-md text-[10px] font-black">{time} Hours (Avg)</span>
                                                </div>
                                              ))
                                            ) : (
                                              <p className="text-xs text-slate-400 italic">Resolution duration not available in this dataset.</p>
                                            )}
                                          </div>
                                        </div>
                                      </div>
                                    )}
                                  </div>
                              ) : (
                                <div className="flex flex-col items-center justify-center py-12 text-center text-slate-400 italic">
                                  <RefreshCcw className="w-8 h-8 animate-spin text-indigo-500 mb-3" />
                                  <p className="text-sm font-medium">Computing analytical insights for this dataset...</p>
                                </div>
                              )
                            ) : (
                              /* AI Analyst Tab Contents */
                              <div className="space-y-8">
                                {/* AI Summary Card */}
                                <div className="bg-gradient-to-r from-indigo-50/50 to-purple-50/30 rounded-3xl border border-indigo-100 p-6">
                                  <h4 className="text-[10px] font-black text-indigo-900 uppercase tracking-widest flex items-center gap-2 mb-3">
                                    <BadgeCheck className="w-4 h-4 text-indigo-600" />
                                    AI Executive Summary
                                  </h4>
                                  {isSummaryLoading ? (
                                    <div className="flex items-center gap-2 py-4 text-xs text-slate-400 font-medium italic">
                                      <RefreshCcw className="w-4 h-4 animate-spin text-indigo-400" />
                                      AI is analyzing dataset trends...
                                    </div>
                                  ) : selectedFileSummary && selectedFileSummary.summary ? (
                                    <p className="text-slate-700 text-sm leading-relaxed font-medium">
                                      {selectedFileSummary.summary}
                                    </p>
                                  ) : (
                                    <p className="text-slate-400 text-xs italic">No executive summary available for this dataset.</p>
                                  )}
                                </div>

                                {/* Recommendations Grid */}
                                <div className="space-y-4">
                                  <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
                                    <ShieldAlert className="w-4 h-4 text-yellow-500" />
                                    Actionable Recommendations
                                  </h4>
                                  {isRecsLoading ? (
                                    <div className="flex items-center gap-2 py-4 text-xs text-slate-400 font-medium italic">
                                      <RefreshCcw className="w-4 h-4 animate-spin text-yellow-400" />
                                      AI is generating practical solutions...
                                    </div>
                                  ) : selectedFileRecs && selectedFileRecs.length > 0 ? (
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                      {selectedFileRecs.map((rec, idx) => (
                                        <div key={idx} className="bg-white border border-slate-200 rounded-2xl p-5 hover:shadow-md transition-all space-y-2.5">
                                          <div className="flex items-start gap-2">
                                            <span className="inline-flex items-center justify-center bg-red-50 text-red-700 text-[10px] font-extrabold px-2 py-0.5 rounded uppercase tracking-wider shrink-0 mt-0.5">Problem</span>
                                            <p className="text-xs font-bold text-slate-800 leading-tight">{rec.problem}</p>
                                          </div>
                                          <div className="flex items-start gap-2 pt-2 border-t border-slate-50">
                                            <span className="inline-flex items-center justify-center bg-green-50 text-green-700 text-[10px] font-extrabold px-2 py-0.5 rounded uppercase tracking-wider shrink-0 mt-0.5">Action</span>
                                            <p className="text-xs font-semibold text-slate-600 leading-relaxed">{rec.recommendation}</p>
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  ) : (
                                    <p className="text-slate-400 text-xs italic">No suggestions calculated.</p>
                                  )}
                                </div>

                                {/* AIOps Problem Candidates Panel */}
                                {selectedFileInsights && selectedFileInsights.problem_candidates && selectedFileInsights.problem_candidates.length > 0 && (
                                  <div className="space-y-4">
                                    <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
                                      <ShieldAlert className="w-4 h-4 text-red-500" />
                                      AIOps Problem Candidates
                                    </h4>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                      {selectedFileInsights.problem_candidates.map((cand: any) => (
                                        <div key={cand.id} className="bg-white border border-slate-200 rounded-2xl p-5 hover:shadow-md transition-all flex flex-col justify-between space-y-4 shadow-sm">
                                          <div className="space-y-2">
                                            <div className="flex items-center justify-between">
                                              <span className={`px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-wider border ${
                                                cand.type.includes("SLA") 
                                                  ? "bg-red-50 text-red-700 border-red-200" 
                                                  : "bg-orange-50 text-orange-700 border-orange-200"
                                              }`}>
                                                {cand.type}
                                              </span>
                                              <span className="text-xs font-extrabold text-slate-400">{cand.frequency} Events</span>
                                            </div>
                                            <p className="text-xs font-bold text-slate-800 leading-tight">{cand.description}</p>
                                          </div>

                                          <div className="pt-3 border-t border-slate-50 flex items-center justify-between">
                                            <span className="text-[9px] text-slate-400 font-semibold italic">Risk Level: {cand.impacted_priority}</span>
                                            <button 
                                              onClick={() => alert(`Initiating Root Cause Analysis (RCA) pipeline for candidate ${cand.id}.`)}
                                              className="px-3 py-1.5 hover:bg-indigo-50 border border-slate-200 hover:border-indigo-200 text-indigo-600 text-[9px] font-black rounded-lg uppercase tracking-wider transition-all cursor-pointer"
                                            >
                                              Launch RCA
                                            </button>
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Dataset Interactive Q&A */}
                                <div className="bg-slate-50 rounded-3xl border border-slate-200 p-6 space-y-4">
                                  <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
                                    <HelpCircle className="w-4 h-4 text-indigo-500" />
                                    Interactive Q&A Assistant
                                  </h4>
                                  <p className="text-xs text-slate-500 font-medium">
                                    Ask any question about the current dataset and let the AI extract precise answers based on ITSM insights.
                                  </p>
                                  
                                  <div className="flex gap-2.5">
                                    <input
                                      type="text"
                                      placeholder="Ask: 'Which group handles the most critical incidents?'..."
                                      value={questionText}
                                      onChange={(e) => setQuestionText(e.target.value)}
                                      onKeyDown={(e) => {
                                        if (e.key === 'Enter') handleAskQuestion();
                                      }}
                                      className="flex-grow pl-4 pr-4 py-3.5 bg-white border border-slate-200 rounded-2xl text-xs font-medium focus:outline-none focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all shadow-sm"
                                    />
                                    <button
                                      onClick={handleAskQuestion}
                                      disabled={isAsking || !questionText.trim()}
                                      className="px-5 py-3.5 bg-slate-900 text-white font-bold rounded-2xl text-xs flex items-center gap-1.5 hover:bg-slate-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md shrink-0 cursor-pointer"
                                    >
                                      {isAsking ? <RefreshCcw className="w-3.5 h-3.5 animate-spin" /> : null}
                                      Ask AI
                                    </button>
                                  </div>

                                  {answerText && (
                                    <motion.div 
                                      initial={{ opacity: 0, y: 10 }}
                                      animate={{ opacity: 1, y: 0 }}
                                      className="bg-white border border-slate-200 rounded-2xl p-5 space-y-2 mt-4 shadow-sm"
                                    >
                                      <span className="text-[9px] font-black text-indigo-600 uppercase tracking-widest block">Response</span>
                                      <p className="text-slate-800 text-xs font-bold leading-relaxed">{answerText}</p>
                                    </motion.div>
                                  )}
                                </div>
                              </div>
                            )}
                          </motion.div>
                        )}
                      </div>
                    );
                  })()}
                </div>

                {/* Right Column: Detail & Upload Panel */}
                <div className="xl:col-span-4 space-y-6">
                  {/* Selected File Details */}
                  {selectedFileId && (
                    <motion.div 
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6"
                    >
                      {(() => {
                        const file = batchFiles.find(f => f.id === selectedFileId);
                        if (!file) return null;
                        return (
                          <>
                            <div className="flex items-center justify-between mb-6">
                              <h4 className="text-sm font-black text-slate-400 uppercase tracking-widest">File Intelligence</h4>
                              <button 
                                onClick={() => handleDeleteFile(file.id)}
                                className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
                                title="Delete File"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                            
                            <div className="space-y-4 mb-8">
                              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-2xl border border-slate-100">
                                <span className="text-xs font-bold text-slate-500">Current Status</span>
                                <span className={`text-xs font-black uppercase ${file.status === 'Classified' ? 'text-green-600' : 'text-blue-600'}`}>
                                  {file.status === 'Classified' ? 'Analyzed' : file.status}
                                </span>
                              </div>
                              
                              {file.status === 'Uploaded' && (
                                <div className="p-4 bg-indigo-50/50 rounded-2xl border border-indigo-100 space-y-4">
                                  <div className="flex items-center gap-2 mb-2">
                                    <Tag className="w-4 h-4 text-indigo-600" />
                                    <h5 className="text-xs font-bold text-indigo-900">Map Required Fields</h5>
                                  </div>
                                  
                                  <div className="space-y-3">
                                    <div>
                                      <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5">Description Column *</label>
                                      <select 
                                        className="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 text-xs font-medium focus:ring-2 focus:ring-indigo-500/20"
                                        value={columnMapping["Description"] || ""}
                                        onChange={(e) => setColumnMapping(prev => ({ ...prev, "Description": e.target.value }))}
                                      >
                                        <option value="">-- Select Column --</option>
                                        {file.headers?.map(h => <option key={h} value={h}>{h}</option>)}
                                      </select>
                                    </div>
                                    <div>
                                      <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5">Category Column *</label>
                                      <select 
                                        className="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 text-xs font-medium focus:ring-2 focus:ring-indigo-500/20"
                                        value={columnMapping["Category"] || ""}
                                        onChange={(e) => setColumnMapping(prev => ({ ...prev, "Category": e.target.value }))}
                                      >
                                        <option value="">-- Select Column --</option>
                                        {file.headers?.map(h => <option key={h} value={h}>{h}</option>)}
                                      </select>
                                    </div>
                                    <div>
                                      <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5">Subcategory Column</label>
                                      <select 
                                        className="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 text-xs font-medium focus:ring-2 focus:ring-indigo-500/20"
                                        value={columnMapping["Subcategory"] || ""}
                                        onChange={(e) => setColumnMapping(prev => ({ ...prev, "Subcategory": e.target.value }))}
                                      >
                                        <option value="">-- Select Column --</option>
                                        {file.headers?.map(h => <option key={h} value={h}>{h}</option>)}
                                      </select>
                                    </div>
                                    <div>
                                      <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5">Assignment Group Column</label>
                                      <select 
                                        className="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 text-xs font-medium focus:ring-2 focus:ring-indigo-500/20"
                                        value={columnMapping["Assignment_Group"] || ""}
                                        onChange={(e) => setColumnMapping(prev => ({ ...prev, "Assignment_Group": e.target.value }))}
                                      >
                                        <option value="">-- Select Column --</option>
                                        {file.headers?.map(h => <option key={h} value={h}>{h}</option>)}
                                      </select>
                                    </div>
                                  </div>
                                  
                                  <button 
                                    onClick={() => handleProcessBatch(file.id)}
                                    disabled={isUploading || !columnMapping["Description"] || !columnMapping["Category"]}
                                    className="w-full py-4 bg-indigo-600 text-white rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-indigo-700 shadow-lg shadow-indigo-100 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                  >
                                    {isUploading ? <RefreshCcw className="w-4 h-4 animate-spin" /> : <Activity className="w-4 h-4" />}
                                    Run Analytics & Insights
                                  </button>
                                  {(!columnMapping["Description"] || !columnMapping["Category"]) && (
                                    <p className="text-[10px] text-red-500 font-bold text-center italic">Map Description and Category columns to enable analysis</p>
                                  )}
                                </div>
                              )}
                              
                              {file.status === 'Classified' && (
                                <div className="space-y-4">
                                  {/* Read-Only Column Mapping Panel */}
                                  <div className="p-4 bg-slate-50 border border-slate-200/60 rounded-2xl space-y-3">
                                    <div className="flex items-center gap-2 mb-1.5 pb-2 border-b border-slate-200/50">
                                      <BadgeCheck className="w-4 h-4 text-green-600" />
                                      <h5 className="text-[11px] font-black text-slate-800 uppercase tracking-wider">Active Column Mapping</h5>
                                    </div>
                                    <div className="grid grid-cols-2 gap-2 text-[10px]">
                                      <div>
                                        <span className="font-extrabold text-slate-400 uppercase block tracking-wider">Description</span>
                                        <span className="font-bold text-slate-700 truncate block">{file.column_mapping?.["Description"] || "Auto-detected"}</span>
                                      </div>
                                      <div>
                                        <span className="font-extrabold text-slate-400 uppercase block tracking-wider">Category</span>
                                        <span className="font-bold text-slate-700 truncate block">{file.column_mapping?.["Category"] || "Auto-detected"}</span>
                                      </div>
                                      <div>
                                        <span className="font-extrabold text-slate-400 uppercase block tracking-wider">Subcategory</span>
                                        <span className="font-bold text-slate-700 truncate block">{file.column_mapping?.["Subcategory"] || "N/A"}</span>
                                      </div>
                                      <div>
                                        <span className="font-extrabold text-slate-400 uppercase block tracking-wider">Assignment Group</span>
                                        <span className="font-bold text-slate-700 truncate block">{file.column_mapping?.["Assignment_Group"] || "N/A"}</span>
                                      </div>
                                    </div>
                                  </div>



                                  <button 
                                    onClick={async () => {
                                      try {
                                        const res = await fetch(`/api/batch/files/${file.id}/sop`);
                                        if (res.ok) {
                                          const blob = await res.blob();
                                          const url = window.URL.createObjectURL(blob);
                                          const a = document.createElement('a');
                                          a.href = url;
                                          a.download = `SOP_${file.filename.split('.')[0]}.md`;
                                          document.body.appendChild(a);
                                          a.click();
                                          a.remove();
                                        } else {
                                          alert("Failed to generate SOP document. Please try again.");
                                        }
                                      } catch (err) {
                                        console.error("SOP generation failed", err);
                                        alert("An error occurred during SOP generation.");
                                      }
                                    }}
                                    className="w-full py-4 bg-indigo-600 text-white rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-indigo-700 shadow-xl shadow-indigo-100 transition-all cursor-pointer"
                                  >
                                    <FileSpreadsheet className="w-4 h-4" />
                                    Export SOP Documents
                                  </button>
                                </div>
                              )}
                            </div>


                          </>
                        );
                      })()}
                    </motion.div>
                  )}

                  {/* Upload Section */}
                  <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6">
                    <h4 className="text-sm font-black text-slate-400 uppercase tracking-widest mb-6">Queue New Batch</h4>
                    <div 
                      className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all relative ${
                        batchFile ? 'border-indigo-400 bg-indigo-50/30' : 'border-slate-200 hover:border-indigo-300 bg-slate-50'
                      }`}
                    >
                      <input 
                        type="file" 
                        accept=".csv, .xlsx"
                        onChange={(e) => {
                          setBatchFile(e.target.files?.[0] || null);
                          setUploadMessage(null);
                        }}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        disabled={isUploading}
                      />
                      <UploadCloud className={`w-8 h-8 mx-auto mb-3 ${batchFile ? 'text-indigo-600' : 'text-slate-300'}`} />
                      <p className="text-xs font-bold text-slate-900 mb-1">
                        {batchFile ? batchFile.name : 'Click to Upload'}
                      </p>
                      <p className="text-[10px] text-slate-400 uppercase font-black tracking-widest">.xlsx or .csv</p>
                    </div>

                    {uploadMessage && (
                      <div className={`mt-4 p-3 rounded-xl flex items-center gap-2 ${uploadMessage.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                        {uploadMessage.type === 'success' ? <CheckCircle2 className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
                        <span className="font-bold text-[10px]">{uploadMessage.text}</span>
                      </div>
                    )}

                    <button 
                      onClick={handleBatchUpload}
                      disabled={!batchFile || isUploading}
                      className="w-full mt-6 py-4 bg-slate-900 text-white rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-slate-800 disabled:opacity-50 transition-all shadow-xl shadow-slate-200"
                    >
                      {isUploading ? <RefreshCcw className="w-4 h-4 animate-spin" /> : <UploadCloud className="w-4 h-4" />}
                      {isUploading ? 'Uploading...' : 'Confirm Upload'}
                    </button>
                  </div>
                </div>
              </motion.div>
            )}

            {currentView === 'team' && (
              <motion.div
                key="team"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="max-w-4xl mx-auto"
              >
                <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
                  <div className="p-8 border-b border-slate-100">
                    <h3 className="text-2xl font-bold text-slate-900 mb-2">ServiceNow IT Directory</h3>
                    <p className="text-slate-500 font-medium">Auto-synced snapshot of IT users from ServiceNow table sys_user.</p>
                  </div>
                  <div className="divide-y divide-slate-100">
                    {teamMembers.map((member) => (
                      <div key={member.id} className="p-6 flex items-center justify-between hover:bg-slate-50 transition-colors">
                        <div className="flex items-center gap-4">
                          <div className="w-12 h-12 rounded-2xl bg-slate-100 flex items-center justify-center text-indigo-600 font-bold text-lg">
                            {member.name.split(' ').map(n => n[0]).join('').substring(0, 2)}
                          </div>
                          <div>
                            <h4 className="font-bold text-slate-900">{member.name}</h4>
                            <p className="text-sm text-slate-500 font-medium line-clamp-1">{member.role}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-6">
                          <div className="hidden md:flex items-center gap-2 text-sm text-slate-400 font-medium">
                            <Mail className="w-4 h-4" />
                            {member.email || "No email"}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}

            {currentView === 'profile' && (
              <motion.div
                key="profile"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="max-w-2xl mx-auto"
              >
                <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
                  <div className="h-32 bg-indigo-600 relative">
                    <div className="absolute -bottom-12 left-8 w-24 h-24 rounded-3xl bg-white p-1 shadow-xl">
                      <div className="w-full h-full rounded-2xl bg-indigo-100 flex items-center justify-center text-indigo-600 text-3xl font-black">KK</div>
                    </div>
                  </div>
                  <div className="pt-16 p-8">
                    <div className="flex items-center justify-between mb-8">
                      <div>
                        <h3 className="text-2xl font-bold text-slate-900">Kaavviya K.</h3>
                        <p className="text-slate-500 font-medium">Lead Operations Engineer</p>
                      </div>
                      <span className="px-4 py-1.5 bg-green-50 text-green-700 border border-green-100 rounded-full text-xs font-bold uppercase tracking-wider">Active</span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Employee ID</label>
                        <div className="flex items-center gap-2 text-slate-700 font-bold"><Hash className="w-4 h-4 text-slate-300" /> EMP-99821</div>
                      </div>
                      <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Contact Email</label>
                        <div className="flex items-center gap-2 text-slate-700 font-bold"><Mail className="w-4 h-4 text-slate-300" /> kaavviya22@gmail.com</div>
                      </div>
                      <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Department</label>
                        <div className="flex items-center gap-2 text-slate-700 font-bold"><BadgeCheck className="w-4 h-4 text-slate-300" /> IT Operations</div>
                      </div>
                      <div className="space-y-1">
                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Access Level</label>
                        <div className="flex items-center gap-2 text-slate-700 font-bold"><ShieldAlert className="w-4 h-4 text-slate-300" /> Administrator</div>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {currentView === 'help' && (
              <motion.div
                key="help"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="max-w-4xl mx-auto space-y-8"
              >
                <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-8">
                  <h3 className="text-2xl font-bold text-slate-900 mb-6 flex items-center gap-3">
                    <Info className="text-indigo-600 w-8 h-8" />
                    How to use IncidentControl
                  </h3>
                  <div className="space-y-6 text-slate-600 font-medium leading-relaxed">
                    <p>Welcome to the IT Operations Dashboard. This platform is designed to streamline incident management and team collaboration with AI automated routing.</p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="p-6 bg-slate-50 rounded-2xl border border-slate-100">
                        <h4 className="font-bold text-slate-900 mb-3 flex items-center gap-2">
                          <ShieldAlert className="w-4 h-4 text-yellow-600" /> Classify
                        </h4>
                        <p className="text-sm">Click 'Classify' to use Gemini LLM to categorize new incidents to determine their scope and impact automatically based on the description.</p>
                      </div>
                      <div className="p-6 bg-slate-50 rounded-2xl border border-slate-100">
                        <h4 className="font-bold text-slate-900 mb-3 flex items-center gap-2">
                          <UserPlus className="w-4 h-4 text-blue-600" /> Assign
                        </h4>
                        <p className="text-sm">Click 'Assign' to pull live ServiceNow users/groups and have Gemini route the ticket accurately. The result is patched to ServiceNow work notes dynamically.</p>
                      </div>
                      <div className="p-6 bg-slate-50 rounded-2xl border border-slate-100">
                        <h4 className="font-bold text-slate-900 mb-3 flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-green-600" /> Resolve
                        </h4>
                        <p className="text-sm">Complete the UI lifecycle simulation by resolving the ticket and concluding the loop.</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-indigo-600 rounded-3xl p-8 text-white flex items-center justify-between shadow-xl shadow-indigo-200">
                  <div>
                    <h4 className="text-xl font-bold mb-2">Need further assistance?</h4>
                    <p className="text-indigo-100 font-medium">Contact our 24/7 internal support line or visit the documentation.</p>
                  </div>
                  <button className="px-6 py-3 bg-white text-indigo-600 rounded-2xl font-bold flex items-center gap-2 hover:bg-indigo-50 transition-all">
                    View Docs <ExternalLink className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
