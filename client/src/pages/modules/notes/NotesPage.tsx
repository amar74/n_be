import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useNotes } from '@/hooks/useNotes';
import { Note } from '@/types/notes';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
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
import { Input } from '@/components/ui/input';
import { Search, Plus, Calendar, Edit, Trash2, FileText } from 'lucide-react';
import { format } from 'date-fns';

export default function NotesPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const limit = 12;

  const { notes, totalCount, isLoading, isDeleting, deleteNote, refetch } = useNotes({
    page,
    limit,
  });

  const handleDeleteNote = (noteId: string) => {
    deleteNote(noteId);
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const filteredNotes = notes.filter((note) =>
    note.meeting_title.toLowerCase().includes(search.toLowerCase())
  );

  const totalPages = Math.ceil(totalCount / limit);

  if (isLoading) {
    return (
      <div className="container mx-auto py-8">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">Meeting Notes</h1>
          <p className="text-muted-foreground">
            Manage your organization's meeting notes and minutes
          </p>
        </div>
        <Button asChild>
          <Link to="/module/notes/create">
            <Plus className="mr-2 h-4 w-4" />
            New Note
          </Link>
        </Button>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search notes..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Notes Grid */}
      {filteredNotes.length === 0 ? (
        <Card className="text-center py-12">
          <CardContent>
            <FileText className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No notes found</h3>
            <p className="text-muted-foreground mb-4">
              {search
                ? 'No notes match your search criteria'
                : 'Get started by creating your first meeting note'}
            </p>
            {!search && (
              <Button asChild>
                <Link to="/module/notes/create">
                  <Plus className="mr-2 h-4 w-4" />
                  Create First Note
                </Link>
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredNotes.map((note) => (
            <NoteCard
              key={note.id}
              note={note}
              onDelete={handleDeleteNote}
              isDeleting={isDeleting}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-2">
          <Button
            variant="outline"
            onClick={() => handlePageChange(page - 1)}
            disabled={page <= 1}
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            onClick={() => handlePageChange(page + 1)}
            disabled={page >= totalPages}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}

interface NoteCardProps {
  note: Note;
  onDelete: (id: string) => void;
  isDeleting: boolean;
}

function NoteCard({ note, onDelete, isDeleting }: NoteCardProps) {
  const meetingDate = new Date(note.meeting_datetime);
  const createdDate = new Date(note.created_at);

  return (
    <Card className="flex flex-col">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="space-y-1 flex-1">
            <CardTitle className="text-lg leading-tight">{note.meeting_title}</CardTitle>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar className="h-4 w-4" />
              {format(meetingDate, 'MMM dd, yyyy • h:mm a')}
            </div>
          </div>
          <Badge variant="secondary" className="shrink-0">
            <FileText className="mr-1 h-3 w-3" />
            Note
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="flex-1">
        <p className="text-sm text-muted-foreground line-clamp-3">
          {note.meeting_notes.length > 150
            ? `${note.meeting_notes.substring(0, 150)}...`
            : note.meeting_notes}
        </p>
      </CardContent>

      <CardFooter className="flex items-center justify-between pt-4">
        <div className="text-xs text-muted-foreground">
          Created {format(createdDate, 'MMM dd, yyyy')}
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" asChild>
            <Link to={`/module/notes/${note.id}`}>
              View
            </Link>
          </Button>
          <Button variant="outline" size="sm" asChild>
            <Link to={`/module/notes/${note.id}/edit`}>
              <Edit className="h-4 w-4" />
            </Link>
          </Button>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="outline" size="sm" disabled={isDeleting}>
                <Trash2 className="h-4 w-4" />
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
                  onClick={() => onDelete(note.id)}
                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                >
                  Delete
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </CardFooter>
    </Card>
  );
}
