import { useFormbricksSurveys } from "@/hooks/use-formbricks";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

function ClientSurveys() {
    const { data, isLoading, error, createSurvey, creating } = useFormbricksSurveys();
    const navigate = useNavigate();

    const [open, setOpen] = useState(false);
    const [name, setName] = useState("");
    const [submitError, setSubmitError] = useState<string | null>(null);

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

    return (
        <div className="flex-1 min-h-0 w-full flex flex-col p-4">
            <div className="flex items-center justify-between mb-4">
                <h1 className="text-2xl font-bold">Surveys</h1>
                <Dialog open={open} onOpenChange={setOpen}>
                    <DialogTrigger asChild>
                        <Button>Create Survey</Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[640px]">
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
            <ul className="space-y-4">
                {surveys?.map((survey) => (
                    <li
                        key={survey.id}
                        className="border rounded-lg p-4 shadow-md"
                        onClick={() => navigate(`/client-surveys/${survey.environment_id}/${survey.id}`)}
                    >
                        <h2 className="text-xl font-semibold">{survey.name}</h2>
                        <p className="text-gray-600">Created At: {new Date(survey.createdAt).toLocaleDateString()}</p>
                        <p className="text-gray-600">Environment Id: {survey.environment_id}</p>
                        <p className="text-gray-600">Updated At: {new Date(survey.updatedAt).toLocaleDateString()}</p>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default ClientSurveys;