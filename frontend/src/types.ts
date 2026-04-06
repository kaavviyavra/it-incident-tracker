export type Priority = 'Low' | 'Medium' | 'High' | 'Critical';
export type Status = 'Open' | 'Assigned' | 'Resolved' | 'Classified';
export type Category = 'Network' | 'Application' | 'Infrastructure';

export interface Incident {
  id: string;
  description: string;
  priority: Priority;
  status: Status;
  category?: Category;
  createdAt: string;
  assignedTo?: string;
}

export interface TeamMember {
  id: string;
  name: string;
  role: string;
  email: string;
  avatar?: string;
}
