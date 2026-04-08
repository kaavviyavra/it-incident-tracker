export type Priority = string;
export type Status = 'Open' | 'Assigned' | 'Resolved' | 'Classified';
export type Category = string;

export interface Incident {
  id: string;
  description: string;
  priority: Priority;
  status: Status;
  category?: Category;
  subcategory?: string;
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
