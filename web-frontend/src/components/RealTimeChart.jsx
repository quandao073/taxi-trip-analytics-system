import {
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer
} from 'recharts';

export default function RealTimeChart({ data }) {
  return (
    <div style={{ height: 500, marginTop: 50 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="pickup_zone" interval={0} angle={-30} textAnchor="end" height={100} tick={{ fontSize: 12 }} />
          <YAxis />
          <Tooltip 
            formatter={(value) => [value.toFixed(2), 'USD']}
            contentStyle={{
              backgroundColor: '#333',
              border: 'none',
              borderRadius: 5,
              color: '#fff'
            }}
          />
          <Bar dataKey="total_revenue" fill="#82ca9d" name="Total Revenue" animationDuration={300} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
