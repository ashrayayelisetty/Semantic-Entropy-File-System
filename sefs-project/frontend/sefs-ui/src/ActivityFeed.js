import React from 'react';

function ActivityFeed({ activities }) {
  return (
    <div style={{
      position: 'absolute',
      top: 120,
      left: 20,
      background: 'white',
      padding: 15,
      borderRadius: 8,
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      maxWidth: 300,
      maxHeight: 400,
      overflow: 'auto'
    }}>
      <h3 style={{ margin: '0 0 10px 0', fontSize: 16 }}>📊 Activity Feed</h3>
      {activities.length === 0 ? (
        <p style={{ color: '#999', fontSize: 14 }}>No recent activity</p>
      ) : (
        <div>
          {activities.map(activity => (
            <div
              key={activity.id}
              style={{
                padding: '8px',
                borderBottom: '1px solid #eee',
                fontSize: 13
              }}
            >
              <span style={{ marginRight: 8 }}>{activity.icon}</span>
              <span>{activity.message}</span>
              <div style={{ color: '#999', fontSize: 11, marginTop: 3 }}>
                {activity.time}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ActivityFeed;
