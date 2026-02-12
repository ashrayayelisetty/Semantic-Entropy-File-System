import React from 'react';

function ActivityFeed({ activities }) {
  return (
    <div className="activity-feed">
      <h3>📊 Activity Feed</h3>
      {activities.length === 0 ? (
        <p className="activity-empty">No recent activity</p>
      ) : (
        <div>
          {activities.map(activity => (
            <div key={activity.id} className="activity-item">
              <span className="activity-icon">{activity.icon}</span>
              <div className="activity-content">
                <div className="activity-message">{activity.message}</div>
                <div className="activity-time">{activity.time}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ActivityFeed;
