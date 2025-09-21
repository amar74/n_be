import { useFormbricksSurveys } from "@/hooks/use-formbricks";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { CalendarDays, Clock, MoreVertical } from "lucide-react";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

function ClientSurveys() {
    const { data, isLoading, error, createSurvey, creating } = useFormbricksSurveys();
    const navigate = useNavigate();

    const [open, setOpen] = useState(false);
    const [name, setName] = useState("");
    const [submitError, setSubmitError] = useState<string | null>(null);
    const [query, setQuery] = useState("");

    async function onCreateSurvey(e: React.FormEvent) {
        e.preventDefault();
        setSubmitError(null);
        try {
            await createSurvey({ name });
            setOpen(false);
            setName("");
        } catch (err: any) {
            setSubmitError(err?.message || "Failed to create survey");
        }
    }

    if (isLoading || !data) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Error: {error?.message}</div>;
    }

    const { surveys } = data;
    const filtered = (surveys || []).filter((s) =>
        s.name.toLowerCase().includes(query.toLowerCase()) ||
        s.environment_id.toLowerCase().includes(query.toLowerCase())
    );

    return (
        <div className="flex-1 min-h-0 w-full flex flex-col gap-4 p-6">
            <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                    <h1 className="text-2xl font-semibold tracking-tight">Surveys</h1>
                    <span className="text-xs text-gray-500">{filtered.length} total</span>
                </div>
                <Dialog open={open} onOpenChange={setOpen}>
                    <DialogTrigger asChild>
                        <Button>Create Survey</Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[640px] z-[1000] bg-white">
                        <DialogHeader>
                            <DialogTitle>Create New Survey</DialogTitle>
                        </DialogHeader>
                        <form onSubmit={onCreateSurvey} className="space-y-3">
                            <div className="space-y-1">
                                <Label htmlFor="name">Name</Label>
                                <Input id="name" value={name} onChange={(e) => setName(e.target.value)} required />
                            </div>
                            {/* Defaults applied server-side; only name is required */}
                            {submitError && <div className="text-red-600 text-sm">{submitError}</div>}
                            <div className="flex justify-end gap-2 pt-2">
                                <Button type="button" variant="secondary" onClick={() => setOpen(false)}>Cancel</Button>
                                <Button type="submit" disabled={creating}>Create</Button>
                            </div>
                        </form>
                    </DialogContent>
                </Dialog>
            </div>

            <div className="flex items-center gap-3">
                <div className="relative w-full sm:max-w-md">
                    <Input
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search by name or environment..."
                        className="pl-3 pr-3"
                    />
                </div>
            </div>

            <ul className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
                {filtered.map((survey) => (
                    <li
                        key={survey.id}
                        className="group rounded-xl border bg-white shadow-sm transition hover:shadow-md"
                    >
                        <div className="p-5 pb-3 flex items-start justify-between gap-3">
                            <div className="min-w-0">
                                <h2 className="text-base font-semibold truncate" title={survey.name}>{survey.name}</h2>
                                <div className="mt-2 flex flex-wrap items-center gap-4 text-xs text-gray-500">
                                    <span className="inline-flex items-center gap-1">
                                        <CalendarDays className="h-3.5 w-3.5" />
                                        Created {new Date(survey.createdAt).toLocaleDateString()}
                                    </span>
                                    <span className="inline-flex items-center gap-1">
                                        <Clock className="h-3.5 w-3.5" />
                                        Updated {new Date(survey.updatedAt).toLocaleDateString()}
                                    </span>
                                </div>
                            </div>
                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button variant="ghost" size="icon" className="h-8 w-8 shrink-0">
                                        <MoreVertical className="h-5 w-5" />
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end" className="bg-white">
                                    <DropdownMenuItem onClick={() => navigate(`/client-surveys/${survey.environment_id}/${survey.id}`)}>
                                        Show
                                    </DropdownMenuItem>
                                    <DropdownMenuItem onClick={() => navigate(`/client-surveys/${survey.environment_id}/${survey.id}/edit`)}>
                                        Edit
                                    </DropdownMenuItem>
                                    <DropdownMenuItem
                                        className="text-red-600 focus:text-red-600"
                                        onClick={() => {
                                            if (confirm(`Delete survey \"${survey.name}\"?`)) {
                                                alert("Delete is not implemented yet");
                                            }
                                        }}
                                    >
                                        Delete
                                    </DropdownMenuItem>
                                </DropdownMenuContent>
                            </DropdownMenu>
                        </div>
                        <div className="px-5 pb-4 pt-3 border-t text-xs text-gray-600">
                            <span className="font-medium mr-1">Environment:</span>
                            <code className="rounded bg-gray-50 px-1.5 py-0.5 text-[11px]">{survey.environment_id}</code>
                        </div>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default ClientSurveys;