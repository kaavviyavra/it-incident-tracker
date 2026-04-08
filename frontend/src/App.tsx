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
  Tag
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { Incident, Priority, Status, TeamMember, Category } from './types';

type View = 'dashboard' | 'profile' | 'help' | 'team';

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

  const fetchIncidents = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/incidents');
      if (!response.ok) throw new Error('Failed to connect to the incident management server.');
      
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

  useEffect(() => {
    fetchIncidents();
    fetchTeam();
  }, []);

  const addToHistory = (message: string) => {
    setHistory(prev => [{
      id: Math.random().toString(36).substring(2, 9),
      message,
      timestamp: new Date()
    }, ...prev].slice(0, 50));
  };
  
  // API Flow Actions
  const handleClassify = async (incident: Incident) => {
    addToHistory(`Classifying ${incident.id} using Gemini...`);
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

        <div className="p-4 border-t border-slate-100">
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-slate-500 hover:bg-red-50 hover:text-red-600 transition-all font-bold text-sm">
            <LogOut className="w-5 h-5 shrink-0" />
            {isSidebarOpen && <span>Sign Out</span>}
          </button>
        </div>
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
