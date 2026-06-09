import { useMemo } from 'react';

import { ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { TooltipProps } from 'recharts';


interface NutritionDataPoint {
 id: string;
 name: string;
 minRange: number;
 maxRange: number | null;
 renderMax: number;
 actualValue: number;
 status: 'below' | 'within' | 'above';
 unit: string;
 diseases?: string[];
 source?: string;
 basis?: string;
}

interface NutritionChartProps {
 data: Array<{
 nutrient: string;
 min: number;
 max: number | null;
 actual: number;
 unit?: string;
 diseases?: string[];
 source?: string;
 basis?: string;
 }>;
 unit?: string;
}

const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
 if (!active || !payload || payload.length === 0) return null;

 const data = payload[0].payload as NutritionDataPoint;

 const tLocal = {
 below: 'Below Range',
 within: 'Within Range',
 above: 'Above Range',
 noLimit: 'No limit',
 limitationSource: 'Limitation Basis',
 normalNeeds: 'Normal Needs',
 recommendedRange: 'Recommended Range',
 combinedDiseases: 'Combined Diseases',
 diseases: {
 normal: 'Normal Needs',
 dm2: 'Diabetes Mellitus Type 2',
 hypertension: 'Hypertension',
 cvd: 'Cardiovascular Disease',
 cholesterol: 'High Cholesterol',
 ckd: 'Chronic Kidney Disease',
 } as Record<string, string>
 };

 const getStatusBadge = (status: string) => {
 if (status === 'below') {
 return (
 <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-yellow-100 text-yellow-800 border border-yellow-250 ">
 ⬇ {tLocal.below}
 </span>
 );
 }
 if (status === 'within') {
 return (
 <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-100 text-emerald-855 border border-emerald-200 ">
 ✓ {tLocal.within}
 </span>
 );
 }
 return (
 <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-red-100 text-red-850 border border-red-200 ">
 ⬆ {tLocal.above}
 </span>
 );
 };

 // Format the limit source / diseases
 const getLimitationLabel = () => {
 if (data.diseases && data.diseases.length > 0) {
 if (data.diseases.length >= 3) {
 return tLocal.combinedDiseases;
 }
 // Map disease code to readable full name
 const diseaseNames = data.diseases.map(d => {
 const key = d.toLowerCase().trim();
 return tLocal.diseases[key] || d;
 });
 return diseaseNames.join(' & ');
 }
 
 return tLocal.normalNeeds;
 };

 const limitText = getLimitationLabel();

 // Range formatting
 const maxText = data.maxRange !== null && Number.isFinite(data.maxRange) 
 ? `${data.maxRange}${data.unit}` 
 : tLocal.noLimit;
 const minText = `${data.minRange}${data.unit}`;

 const getThemeStyles = (status: string) => {
 if (status === 'below') {
 return {
 cardBorder: 'border-yellow-400 ',
 cardBg: 'bg-yellow-50/90 ',
 actualText: 'text-yellow-600 '
 };
 }
 if (status === 'within') {
 return {
 cardBorder: 'border-emerald-400 ',
 cardBg: 'bg-emerald-50/90 ',
 actualText: 'text-emerald-600 '
 };
 }
 return {
 cardBorder: 'border-red-400 ',
 cardBg: 'bg-red-50/90 ',
 actualText: 'text-red-600 '
 };
 };

 const cardTheme = getThemeStyles(data.status);

 return (
 <div className={`backdrop-blur-md border-2 ${cardTheme.cardBorder} ${cardTheme.cardBg} rounded-2xl p-3 shadow-xl max-w-[260px] font-sans transition-all`}>
 <div className="flex items-center justify-between gap-3 mb-2">
 <p className="font-bold text-slate-900 text-sm tracking-tight">{label}</p>
 {getStatusBadge(data.status)}
 </div>
 
 <div className="space-y-2 text-xs border-t border-slate-200/50 pt-2">
 <div className="flex flex-col text-left">
 <span className="text-slate-500 font-medium">{tLocal.recommendedRange}</span>
 <span className="text-slate-800 font-semibold text-sm">{minText} - {maxText}</span>
 </div>
 
 <div className="flex flex-col text-left border-t border-slate-200/30 pt-1.5">
 <span className="text-slate-500 font-medium">Actual</span>
 <span className={`font-bold text-sm ${cardTheme.actualText}`}>{data.actualValue}{data.unit}</span>
 </div>

 <div className="border-t border-slate-200/50 pt-1.5 flex flex-col gap-0.5 text-left">
 <span className="text-[9px] text-slate-450 font-bold uppercase tracking-wider">
 {tLocal.limitationSource}
 </span>
 <span className="text-[11px] text-slate-700 font-semibold bg-white/50 px-2 py-0.5 rounded-lg border border-slate-200/30 ">
 {limitText}
 </span>
 </div>
 </div>
 </div>
 );
};

const CustomDot = (props: any) => {
 const { cx, cy, payload } = props;

 if (!payload || typeof cx !== 'number' || typeof cy !== 'number') return null;

 let fill = '#059669';
 if (payload.status === 'below') fill = '#eab308';
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

const CustomActiveDot = (props: any) => {
 const { cx, cy, payload } = props;

 if (!payload || typeof cx !== 'number' || typeof cy !== 'number') return null;

 let fill = '#059669';
 if (payload.status === 'below') fill = '#eab308';
 if (payload.status === 'above') fill = '#dc2626';

 return (
 <circle
 cx={cx}
 cy={cy}
 r={9}
 fill={fill}
 stroke="#fff"
 strokeWidth={3}
 style={{ filter: 'drop-shadow(0px 2px 4px rgba(0,0,0,0.15))' }}
 />
 );
};

export function NutritionChart({ data, unit = 'g' }: NutritionChartProps) {
 const chartData: NutritionDataPoint[] = useMemo(() => {
 return data.map((item, index) => {
 let status: 'below' | 'within' | 'above' = 'within';
 if (item.actual < item.min) status = 'below';
 else if (item.max !== null && item.actual > item.max) status = 'above';

 const id = `nutrient-${index}-${item.nutrient.toLowerCase().replace(/\s+/g, '-')}`;

 // Visual maximum to fill the area indefinitely if there is no actual maximum
 const visualMax = (item.max !== null && Number.isFinite(item.max)) ? item.max : Math.max(item.actual, item.min) * 1.5;

 return {
 id,
 name: item.nutrient,
 minRange: item.min,
 maxRange: item.max,
 renderMax: visualMax,
 actualValue: item.actual,
 status,
 unit: item.unit || unit,
 diseases: item.diseases,
 source: item.source,
 basis: item.basis,
 };
 });
 }, [data, unit]);

 const minAreaFill = '#f0fdf4';

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
 className=""
 />

 <XAxis
 dataKey="name"
 stroke="#6b7280"
 className=""
 tick={{ fill: '#6b7280', fontSize: 10 }}
 tickLine={{ stroke: '#6b7280' }}
 angle={-15}
 textAnchor="end"
 height={60}
 />

 <YAxis
 stroke="#6b7280"
 className=""
 tick={{ fill: '#6b7280', fontSize: 10 }}
 tickLine={{ stroke: '#6b7280' }}
 width={50}
 />

 <Tooltip content={<CustomTooltip />} />

 {/* Area 1: Dari 0 sampai renderMax (background hijau) */}
 <Area
 type="monotone"
 dataKey="renderMax"
 stroke="#10b981"
 strokeWidth={2}
 strokeDasharray="5 5"
 fill="url(#nutritionRangeGradient)"
 fillOpacity={1}
 isAnimationActive={false}
 />

 {/* Area 2: Dari 0 sampai min (untuk "potong" bagian bawah, jadi hanya area antara min-max yang terlihat) */}
 <Area
 type="monotone"
 dataKey="minRange"
 stroke="#10b981"
 strokeWidth={2}
 strokeDasharray="5 5"
 fill={minAreaFill}
 fillOpacity={1}
 isAnimationActive={false}
 />

 <Line
 type="monotone"
 dataKey="actualValue"
 stroke="#059669"
 strokeWidth={4}
 dot={<CustomDot />}
 activeDot={<CustomActiveDot />}
 isAnimationActive={false}
 />
 </ComposedChart>
 </ResponsiveContainer>
 </div>
 );
}
