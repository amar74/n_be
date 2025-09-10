import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export function FinancialTargetAndPerformance() {
  return (
    <div className="flex flex-col gap-3 mt-2">
      {/* Financial Target & Performance */}
      <Card className="rounded-xl shadow-sm border border-gray-200 bg-white">
        <CardHeader className="py-2 px-4 ">
          <CardTitle className="text-xl font-bold">
            Financial Target & Performance
          </CardTitle>
          <p className="text-xs text-[#A7A7A7] font-normal border-b border-gray-200 pb-3">
            Revenue target and financial performance tracking
          </p>
        </CardHeader>

        <CardContent className="grid grid-cols-1 md:grid-cols-4 gap-4 py-3 px-4">
          {/* Annual Revenue Target */}
          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold text-gray-700">
              Annual Revenue Target
            </label>
            <Input
              placeholder="$ 8.5M"
              className=" placeholder:text-black h-9 text-sm font-medium bg-[#F3F3F3] border-[#E6E6E6]  focus:border-[#FF7B00] focus:outline-none focus:ring-0 focus-visible:ring-0"

            />
          </div>

          {/* Quarterly Target */}
          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold text-gray-700">
              Quarterly Target
            </label>
            <Input
              placeholder="$ 2.1M"
              className="placeholder:text-black h-9 text-sm font-medium bg-[#F3F3F3] border-[#E6E6E6]  focus:border-[#FF7B00] focus:outline-none focus:ring-0 focus-visible:ring-0"

            />
          </div>

          {/* Current Year Actual */}
          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold text-gray-700">
              Current Year Actual
            </label>
            <Input
            //   value="$ 5.9M"
            placeholder="$ 5.9M"
              className="placeholder:text-black h-9 text-sm font-medium bg-[#F3F3F3] border-[#E6E6E6]  focus:border-[#FF7B00] focus:outline-none focus:ring-0 focus-visible:ring-0"
            />
          </div>

          {/* Growth Target */}
          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold text-gray-700">
              Growth Target
            </label>
            <Input
              placeholder="15%"
              className="placeholder:text-black h-9 text-sm font-medium bg-[#F3F3F3] border-[#E6E6E6]  focus:border-[#FF7B00] focus:outline-none focus:ring-0 focus-visible:ring-0"
            />
          </div>
        </CardContent>
      </Card>

      {/* Account Documents */}
      <Card className="rounded-xl shadow-sm border border-gray-200 bg-white">
        <CardHeader className="py-2 px-4">
          <CardTitle className="text-xl font-bold">Account Documents</CardTitle>
          <p className="text-xs text-[#A7A7A7] font-normal border-b border-gray-200 pb-3">
            Upload presentations and documents for this account
          </p>
        </CardHeader>

        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-8 py-3 px-4">
          <div className="flex flex-col items-center justify-center rounded-xl bg-[#F0FDF4] py-6">
            <p className="text-2xl font-bold text-[#167852]">72%</p>
            <p className="text-xs font-semibold text-gray-900 mt-2">Target Achieved</p>
          </div>

          <div className="flex flex-col items-center justify-center rounded-xl bg-[#EFF6FF] py-6">
            <p className="text-2xl font-bold text-[#1E40AF]"> + 18%</p>
            <p className="text-xs font-semibold text-gray-900 mt-2">Revenue Growth</p>
          </div>

          <div className="flex flex-col items-center justify-center rounded-xl bg-[#F0E6F8] py-6">
            <p className="text-2xl font-bold text-[#9333EA]">94%</p>
            <p className="text-xs font-semibold text-gray-900 mt-2">Forecast Accuracy</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
