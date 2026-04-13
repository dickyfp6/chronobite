import React from 'react';
import { Notification } from '../hooks/useNotifications';

interface NotificationsProps {
  notifications: Notification[];
}

export const Notifications: React.FC<NotificationsProps> = ({ notifications }) => {
  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return 'fas fa-check-circle';
      case 'error':
        return 'fas fa-exclamation-circle';
      default:
        return 'fas fa-info-circle';
    }
  };

  const getBgColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-blue-500';
    }
  };

  return (
    <div className="fixed top-4 right-4 z-50 pointer-events-none" style={{ maxWidth: '400px' }}>
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`mb-3 p-4 rounded-lg shadow-lg text-white pointer-events-auto ${getBgColor(
            notification.type
          )}`}
        >
          <i className={`${getIcon(notification.type)} mr-2`}></i>
          <span>{notification.message}</span>
        </div>
      ))}
    </div>
  );
};
