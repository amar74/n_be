import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export function AccountOpportunities() {
  const opportunities = [
    {
      title: "Metro Rail Extension Project",
      stage: "03 - Proposal",
      stageColor: "bg-[#ED8A09] text-white",
      value: "$ 12.5M",
      probability: "85%",
      rfp: "Sep 2025",
      hasProposal: true,
    },
    {
      title: "Bus Rapid Transit System",
      stage: "02 - Qualified",
      stageColor: "bg-[#ED8A09] text-white",
      value: "$ 7.5M",
      probability: "70%",
      rfp: "Jan 2025",
      hasProposal: false,
    },
  ];

  return (
    <Card className="rounded-xl shadow-sm border border-gray-200 bg-white">
      <CardHeader className="pt-2 pb-0 m-0">
        <CardTitle className="text-xl font-bold">
          Account Opportunities
        </CardTitle>
        <p className="text-xs text-[#A7A7A7] font-normal">
          Active and historical opportunities for this account
        </p>
      </CardHeader>

      <CardContent className="flex flex-col gap-2 py-2 px-5 m-0">
        {opportunities.map((opp, idx) => (
          <div
            key={idx}
            className="flex flex-col gap-2 border border-gray-200 rounded-lg p-3"
          >
            {/* Header Row */}
            <div className="flex items-center gap-4">
              <p className="text-sm font-bold text-gray-800">{opp.title}</p>
              <span
                className={`text-xs font-medium px-2 py-0.5 rounded-2xl ${opp.stageColor}`}
              >
                {opp.stage}
              </span>
            </div>

            {/* Details Row */}
            <div className="flex py-2.5 flex-col md:flex-row md:items-center md:justify-between gap-2 border border-[#8C8C8C] rounded-xl p-2">
              <div className="border-r-2 border-gray-200 flex-1 flex justify-center flex-col items-center text-center">
                <p className="text-sm font-semibold text-[#ED8A09] pb-1">Value</p>
                <p className="text-sm font-semibold ">{opp.value}</p>
              </div>

              <div className="hidden md:block w-px bg-gray-300"></div>

              <div className="border-r-2 border-gray-200 flex-1 flex justify-center flex-col items-center text-center">
                <p className="text-sm font-semibold text-[#ED8A09] pb-1">Probability</p>
                <p className="text-sm font-semibold">{opp.probability}</p>
              </div>

              <div className="hidden md:block w-px bg-gray-300"></div>

              <div className="flex-1 flex justify-center flex-col items-center text-center">
                <p className="text-sm font-semibold text-[#ED8A09] pb-1">Expected RFP</p>
                <p className="text-sm font-semibold">{opp.rfp}</p>
              </div>
            </div>

            {/* Actions Row */}
            <div className="flex items-center gap-4 justify-end">
              {opp.hasProposal && (
                <Button className="bg-black text-white rounded-md px-3 h-7 text-xs font-medium">
                  View Proposal
                </Button>
              )}
              <Button
                variant="outline"
                className="rounded-md px-3 h-7 text-xs font-medium"
              >
                click to view opportunity details
              </Button>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
