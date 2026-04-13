import { useMemo } from 'react';
import { ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { TooltipProps } from 'recharts';

interface NutritionDataPoint {
  id: string;
  name: string;
  minRange: number;
  maxRange: number;
  actualValue: number;
  status: 'below' | 'within' | 'above';
}

interface NutritionChartProps {
  data: Array<{
    nutrient: string;
    min: number;
    max: number;
    actual: number;
  }>;
}

const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
  if (!active || !payload || payload.length === 0) return null;

  const data = payload[0].payload as NutritionDataPoint;

  const getStatusColor = (status: string) => {
    if (status === 'below') return 'text-orange-600 dark:text-orange-400';
    if (status === 'within') return 'text-emerald-600 dark:text-emerald-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getStatusText = (status: string) => {
    if (status === 'below') return '⬇ Below Range';
    if (status === 'within') return '✓ Within Range';
    return '⬆ Above Range';
  };

  return (
    <div className="bg-white dark:bg-slate-800 border-2 border-emerald-500 dark:border-emerald-600 rounded-lg p-3 shadow-lg">
      <p className="font-bold text-gray-900 dark:text-white mb-2">{label}</p>
      <div className="space-y-1 text-sm">
        <p className="text-gray-700 dark:text-gray-300">
          <span className="font-medium">Min:</span> {data.minRange}g
        </p>
        <p className="text-gray-700 dark:text-gray-300">
          <span className="font-medium">Max:</span> {data.maxRange}g
        </p>
        <p className="text-emerald-700 dark:text-emerald-300 font-semibold">
          <span className="font-medium">Actual:</span> {data.actualValue}g
        </p>
        <p className={`font-semibold ${getStatusColor(data.status)}`}>
          {getStatusText(data.status)}
        </p>
      </div>
    </div>
  );
};

const CustomDot = (props: any) => {
  const { cx, cy, payload } = props;

  if (!payload || typeof cx !== 'number' || typeof cy !== 'number') return null;

  let fill = '#059669';
  if (payload.status === 'below') fill = '#ea580c';
  if (payload.status === 'above') fill = '#dc2626';

  return (
    <circle
      cx={cx}
      cy={cy}
      r={7}
      fill={fill}
      stroke="#fff"
      strokeWidth={3}
    />
  );
};

export function NutritionChart({ data }: NutritionChartProps) {
  const chartData: NutritionDataPoint[] = useMemo(() => {
    return data.map((item, index) => {
      let status: 'below' | 'within' | 'above' = 'within';
      if (item.actual < item.min) status = 'below';
      else if (item.actual > item.max) status = 'above';

      const id = `nutrient-${index}-${item.nutrient.toLowerCase().replace(/\s+/g, '-')}`;

      return {
        id,
        name: item.nutrient,
        minRange: item.min,
        maxRange: item.max,
        actualValue: item.actual,
        status,
      };
    });
  }, [data]);

  return (
    <div className="w-full h-[350px] sm:h-[400px] md:h-[450px] mb-8">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart
          data={chartData}
          margin={{ top: 10, right: 10, left: 0, bottom: 10 }}
        >
          <defs>
            <linearGradient id="nutritionRangeGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10b981" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#14b8a6" stopOpacity={0.1} />
            </linearGradient>
          </defs>

          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#d1d5db"
            className="dark:stroke-slate-600"
          />

          <XAxis
            dataKey="name"
            stroke="#6b7280"
            className="dark:stroke-gray-400"
            tick={{ fill: '#6b7280', fontSize: 10 }}
            tickLine={{ stroke: '#6b7280' }}
            angle={-15}
            textAnchor="end"
            height={60}
          />

          <YAxis
            stroke="#6b7280"
            className="dark:stroke-gray-400"
            tick={{ fill: '#6b7280', fontSize: 10 }}
            tickLine={{ stroke: '#6b7280' }}
            width={50}
          />

          <Tooltip content={<CustomTooltip />} />

          {/* Area 1: Dari 0 sampai max (background hijau) */}
          <Area
            type="monotone"
            dataKey="maxRange"
            stroke="#10b981"
            strokeWidth={2}
            strokeDasharray="5 5"
            fill="url(#nutritionRangeGradient)"
            fillOpacity={1}
            isAnimationActive={false}
          />

          {/* Area 2: Dari 0 sampai min (background sesuai theme untuk "cut out") */}
          <Area
            type="monotone"
            dataKey="minRange"
            stroke="#10b981"
            strokeWidth={2}
            strokeDasharray="5 5"
            fill="#f0fdf4"
            fillOpacity={1}
            isAnimationActive={false}
            className="dark:fill-slate-900"
          />

          {/* Garis actual value (solid, tebal) - SELALU DI ATAS */}
          <Line
            type="monotone"
            dataKey="actualValue"
            stroke="#059669"
            strokeWidth={4}
            dot={<CustomDot />}
            activeDot={{ r: 9, strokeWidth: 3 }}
            isAnimationActive={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
