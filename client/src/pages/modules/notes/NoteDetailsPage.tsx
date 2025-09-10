import { Link, useParams, useNavigate } from 'react-router-dom';
import { useNote } from '@/hooks/useNotes';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  ArrowLeft, 
  Calendar, 
  Edit, 
  Trash2, 
  FileText, 
  Clock,
  User,
} from 'lucide-react';
import { format } from 'date-fns';

export default function NoteDetailsPage() {
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

  const { note, isLoading, isDeleting, deleteNote, error } = useNote(noteId);

  const handleDeleteNote = () => {
    deleteNote();
    navigate('/module/notes');
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

  const meetingDate = new Date(note.meeting_datetime);
  const createdDate = new Date(note.created_at);
  const updatedDate = note.updated_at ? new Date(note.updated_at) : null;

  return (
    <div className="container mx-auto py-8 max-w-4xl space-y-6">
      {/* Header with Navigation */}
      <div className="flex items-center justify-between">
        <Button variant="outline" asChild>
          <Link to="/module/notes">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Notes
          </Link>
        </Button>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <Link to={`/module/notes/${note.id}/edit`}>
              <Edit className="mr-2 h-4 w-4" />
              Edit
            </Link>
          </Button>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="outline" disabled={isDeleting}>
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete Note</AlertDialogTitle>
                <AlertDialogDescription>
                  Are you sure you want to delete "{note.meeting_title}"? This action cannot be
                  undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction
                  onClick={handleDeleteNote}
                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                >
                  Delete
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </div>

      {/* Note Details */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Badge variant="secondary">
                  <FileText className="mr-1 h-3 w-3" />
                  Meeting Note
                </Badge>
              </div>
              <CardTitle className="text-2xl">{note.meeting_title}</CardTitle>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  <span>{format(meetingDate, 'MMMM dd, yyyy')}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  <span>{format(meetingDate, 'h:mm a')}</span>
                </div>
              </div>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          <Separator />
          
          {/* Meeting Notes Content */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Meeting Notes</h3>
            <div className="prose prose-sm max-w-none">
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {note.meeting_notes}
              </div>
            </div>
          </div>

          <Separator />

          {/* Metadata */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold">Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">Created by:</span>
                  <span className="font-medium">{note.created_by}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">Created:</span>
                  <span className="font-medium">
                    {format(createdDate, 'MMM dd, yyyy • h:mm a')}
                  </span>
                </div>
              </div>
              <div className="space-y-2">
                {updatedDate && (
                  <div className="flex items-center gap-2">
                    <Edit className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Last updated:</span>
                    <span className="font-medium">
                      {format(updatedDate, 'MMM dd, yyyy • h:mm a')}
                    </span>
                  </div>
                )}
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">Note ID:</span>
                  <span className="font-mono text-xs">{note.id}</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
