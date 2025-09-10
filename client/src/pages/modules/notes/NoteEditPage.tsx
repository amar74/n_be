import { useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNote } from '@/hooks/useNotes';
import { NoteUpdateFormData, NoteUpdateFormSchema } from '@/types/notes';
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
import { ArrowLeft, Save, Calendar, FileText } from 'lucide-react';
import { format } from 'date-fns';

export default function NoteEditPage() {
  const { noteId } = useParams<{ noteId: string }>();
  const navigate = useNavigate();

  if (!noteId) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-destructive">Note Not Found</h1>
          <p className="text-muted-foreground mt-2">The requested note could not be found.</p>
          <Button asChild className="mt-4">
            <Link to="/module/notes">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Notes
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  const { note, isLoading, isUpdating, updateNote, error } = useNote(noteId);

  const form = useForm<NoteUpdateFormData>({
    resolver: zodResolver(NoteUpdateFormSchema),
    defaultValues: {
      meeting_title: '',
      meeting_datetime: '',
      meeting_notes: '',
    },
  });

  // Load note data into form when note is fetched
  useEffect(() => {
    if (note) {
      // Convert datetime to local datetime-local format
      const localDateTime = format(new Date(note.meeting_datetime), "yyyy-MM-dd'T'HH:mm");
      
      form.reset({
        meeting_title: note.meeting_title,
        meeting_datetime: localDateTime,
        meeting_notes: note.meeting_notes,
      });
    }
  }, [note, form]);

  const onSubmit = (data: NoteUpdateFormData) => {
    // Convert local datetime back to ISO format
    const updateData = {
      ...data,
      meeting_datetime: data.meeting_datetime 
        ? new Date(data.meeting_datetime).toISOString()
        : undefined,
    };

    updateNote(updateData, {
      onSuccess: () => {
        navigate(`/module/notes/${noteId}`);
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
    navigate(`/module/notes/${noteId}`);
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-8">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  if (error || !note) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-destructive">Error Loading Note</h1>
          <p className="text-muted-foreground mt-2">
            {error?.message || 'Failed to load the note. Please try again.'}
          </p>
          <Button asChild className="mt-4">
            <Link to="/module/notes">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Notes
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 max-w-4xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Edit Note</h1>
          <p className="text-muted-foreground">Update your meeting note details</p>
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
            <FileText className="h-5 w-5" />
            Note Details
          </CardTitle>
          <CardDescription>
            Update the meeting information and notes content
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
                    <FormLabel>Meeting Title</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Enter meeting title"
                        {...field}
                        disabled={isUpdating}
                      />
                    </FormControl>
                    <FormDescription>
                      A clear, descriptive title for the meeting
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
                    <FormLabel>Meeting Date & Time</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Calendar className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                          type="datetime-local"
                          className="pl-10"
                          {...field}
                          disabled={isUpdating}
                        />
                      </div>
                    </FormControl>
                    <FormDescription>
                      When the meeting took place or is scheduled
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
                    <FormLabel>Meeting Notes</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Enter detailed meeting notes, discussions, action items, and outcomes..."
                        className="min-h-[300px] resize-y"
                        {...field}
                        disabled={isUpdating}
                      />
                    </FormControl>
                    <FormDescription>
                      Detailed notes about the meeting content, decisions, and action items
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
                <Button type="submit" disabled={isUpdating}>
                  {isUpdating ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="mr-2 h-4 w-4" />
                      Save Changes
                    </>
                  )}
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
