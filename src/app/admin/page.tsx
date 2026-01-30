/**
 * Admin page - tabbed interface for tile and settings management
 */

'use client';

import { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { TileTable } from '@/components/admin/tile-table';
import { TileForm } from '@/components/admin/tile-form';
import { SettingsForm } from '@/components/admin/settings-form';
import { Plus } from 'lucide-react';
import type { Tile, Settings } from '@/types';

export default function AdminPage() {
  const [tiles, setTiles] = useState<Tile[]>([]);
  const [settings, setSettings] = useState<Settings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  async function fetchTiles() {
    try {
      const response = await fetch('/api/tiles');
      if (!response.ok) throw new Error('Failed to fetch tiles');
      const data = await response.json();
      setTiles(data);
    } catch (error) {
      console.error('Failed to fetch tiles:', error);
    }
  }

  async function fetchSettings() {
    try {
      const response = await fetch('/api/settings');
      if (!response.ok) throw new Error('Failed to fetch settings');
      const data = await response.json();
      setSettings(data);
    } catch (error) {
      console.error('Failed to fetch settings:', error);
    }
  }

  async function fetchData() {
    await Promise.all([fetchTiles(), fetchSettings()]);
    setIsLoading(false);
  }

  useEffect(() => {
    fetchData();
  }, []);

  function handleCreateSuccess() {
    setIsCreateDialogOpen(false);
    fetchTiles();
  }

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold mb-2">Dashboard Management</h2>
        <p className="text-muted-foreground">
          Manage your homelab service tiles and application settings
        </p>
      </div>

      <Tabs defaultValue="tiles" className="space-y-4">
        <TabsList>
          <TabsTrigger value="tiles">Tiles</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="tiles" className="space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-xl font-semibold">Service Tiles</h3>
              <p className="text-sm text-muted-foreground">
                Create and manage your homelab service tiles
              </p>
            </div>
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Tile
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Create New Tile</DialogTitle>
                </DialogHeader>
                <TileForm
                  onSuccess={handleCreateSuccess}
                  onCancel={() => setIsCreateDialogOpen(false)}
                />
              </DialogContent>
            </Dialog>
          </div>

          <TileTable tiles={tiles} onUpdate={fetchTiles} />
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <div>
            <h3 className="text-xl font-semibold mb-4">Application Settings</h3>
            <p className="text-sm text-muted-foreground mb-6">
              Configure your dashboard appearance and behavior
            </p>
          </div>
          {settings && (
            <SettingsForm settings={settings} onSuccess={fetchSettings} />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
