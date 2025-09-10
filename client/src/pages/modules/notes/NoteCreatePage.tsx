import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNotes } from '@/hooks/useNotes';
import { NoteCreateFormData, NoteCreateFormSchema } from '@/types/notes';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { ArrowLeft, Save, Calendar, FileText, Plus } from 'lucide-react';

export default function NoteCreatePage() {
  const navigate = useNavigate();
  const { createNote, isCreating } = useNotes();

  const form = useForm<NoteCreateFormData>({
    resolver: zodResolver(NoteCreateFormSchema),
    defaultValues: {
      meeting_title: '',
      meeting_datetime: '',
      meeting_notes: '',
    },
  });

  const onSubmit = (data: NoteCreateFormData) => {
    // Convert local datetime to ISO format for API
    const createData = {
      ...data,
      meeting_datetime: new Date(data.meeting_datetime).toISOString(),
    };

    createNote(createData, {
      onSuccess: (response) => {
        navigate(`/module/notes/${response.id}`);
      },
    });
  };

  const handleCancel = () => {
    if (form.formState.isDirty) {
      const confirmed = window.confirm(
        'You have unsaved changes. Are you sure you want to leave?'
      );
      if (!confirmed) return;
    }
    navigate('/module/notes');
  };

  return (
    <div className="container mx-auto py-8 max-w-4xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Create New Note</h1>
          <p className="text-muted-foreground">Record meeting notes and important discussions</p>
        </div>
        <Button variant="outline" onClick={handleCancel}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Cancel
        </Button>
      </div>

      {/* Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Plus className="h-5 w-5" />
            New Meeting Note
          </CardTitle>
          <CardDescription>
            Fill in the details about your meeting and add comprehensive notes
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              {/* Meeting Title */}
              <FormField
                control={form.control}
                name="meeting_title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Meeting Title *</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="e.g., Team Standup, Client Review, Project Planning"
                        {...field}
                        disabled={isCreating}
                      />
                    </FormControl>
                    <FormDescription>
                      A clear, descriptive title for the meeting (max 255 characters)
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Meeting Date and Time */}
              <FormField
                control={form.control}
                name="meeting_datetime"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Meeting Date & Time *</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Calendar className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                          type="datetime-local"
                          className="pl-10"
                          {...field}
                          disabled={isCreating}
                        />
                      </div>
                    </FormControl>
                    <FormDescription>
                      When the meeting took place or is scheduled to occur
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Meeting Notes */}
              <FormField
                control={form.control}
                name="meeting_notes"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Meeting Notes *</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder={`Enter detailed meeting notes here. You can include:

• Key discussion points and decisions made
• Action items with assigned owners and deadlines
• Important announcements or updates
• Follow-up items for next meeting
• Questions raised and answers provided
• Any blockers or issues identified

Be as detailed as necessary for future reference.`}
                        className="min-h-[350px] resize-y"
                        {...field}
                        disabled={isCreating}
                      />
                    </FormControl>
                    <FormDescription>
                      Comprehensive notes about the meeting content, decisions, action items, and outcomes (max 10,000 characters)
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Form Actions */}
              <div className="flex items-center justify-end gap-4 pt-6">
                <Button type="button" variant="outline" onClick={handleCancel}>
                  Cancel
                </Button>
                <Button type="submit" disabled={isCreating}>
                  {isCreating ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                      Creating...
                    </>
                  ) : (
                    <>
                      <Save className="mr-2 h-4 w-4" />
                      Create Note
                    </>
                  )}
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>

      {/* Helper Card */}
      <Card className="bg-muted/50">
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Tips for Effective Meeting Notes
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm space-y-2">
          <ul className="space-y-1 text-muted-foreground">
            <li>• Be clear and concise while capturing all important details</li>
            <li>• Include specific action items with owners and deadlines</li>
            <li>• Note any decisions made and their rationale</li>
            <li>• Record questions raised and whether they were resolved</li>
            <li>• Include relevant links, documents, or references discussed</li>
            <li>• Review and save promptly while the meeting is fresh in memory</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
