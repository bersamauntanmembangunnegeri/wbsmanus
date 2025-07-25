import { useState, useEffect } from 'react'
import { Save, Eye, Palette, Type, Layout, Image } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { useAuth } from '../contexts/AuthContext'

export default function AdminLayout() {
  const [layoutSettings, setLayoutSettings] = useState({
    site_title: 'Elite Store',
    site_description: 'Premium Shopping Experience',
    hero_title: 'Discover Your Perfect Style',
    hero_subtitle: 'Explore our curated collection of premium products designed to elevate your lifestyle.',
    hero_cta_primary: 'Shop Now',
    hero_cta_secondary: 'Browse Categories',
    primary_color: '#000000',
    secondary_color: '#666666',
    accent_color: '#0066cc',
    background_color: '#ffffff',
    text_color: '#000000',
    font_family: 'Inter',
    header_layout: 'default',
    footer_layout: 'default',
    logo_url: '',
    favicon_url: '',
    social_facebook: '',
    social_twitter: '',
    social_instagram: '',
    contact_email: 'support@elitestore.com',
    contact_phone: '+1 (555) 123-4567',
    contact_address: '123 Commerce St, City, State 12345'
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const { token } = useAuth()

  useEffect(() => {
    fetchLayoutSettings()
  }, [])

  const fetchLayoutSettings = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/admin/layout', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setLayoutSettings({ ...layoutSettings, ...data })
      }
    } catch (error) {
      console.error('Error fetching layout settings:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setError('')
    setSuccess('')

    try {
      const response = await fetch('/api/admin/layout', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(layoutSettings)
      })

      if (response.ok) {
        setSuccess('Layout settings saved successfully!')
      } else {
        const data = await response.json()
        setError(data.error || 'Failed to save layout settings')
      }
    } catch (error) {
      setError('Network error. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const handleChange = (field, value) => {
    setLayoutSettings({ ...layoutSettings, [field]: value })
    setError('')
    setSuccess('')
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-8">Loading layout settings...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Website Layout</h1>
          <p className="text-muted-foreground">Customize your website appearance and content</p>
        </div>
        
        <div className="flex space-x-2">
          <Button variant="outline">
            <Eye className="h-4 w-4 mr-2" />
            Preview
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            <Save className="h-4 w-4 mr-2" />
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </div>

      {success && (
        <Alert>
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="general" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="hero">Hero Section</TabsTrigger>
          <TabsTrigger value="colors">Colors & Fonts</TabsTrigger>
          <TabsTrigger value="layout">Layout</TabsTrigger>
          <TabsTrigger value="contact">Contact Info</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Layout className="h-5 w-5 mr-2" />
                General Settings
              </CardTitle>
              <CardDescription>
                Basic website information and branding
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="site_title">Site Title</Label>
                  <Input
                    id="site_title"
                    value={layoutSettings.site_title}
                    onChange={(e) => handleChange('site_title', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="site_description">Site Description</Label>
                  <Input
                    id="site_description"
                    value={layoutSettings.site_description}
                    onChange={(e) => handleChange('site_description', e.target.value)}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="logo_url">Logo URL</Label>
                  <Input
                    id="logo_url"
                    type="url"
                    value={layoutSettings.logo_url}
                    onChange={(e) => handleChange('logo_url', e.target.value)}
                    placeholder="https://example.com/logo.png"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="favicon_url">Favicon URL</Label>
                  <Input
                    id="favicon_url"
                    type="url"
                    value={layoutSettings.favicon_url}
                    onChange={(e) => handleChange('favicon_url', e.target.value)}
                    placeholder="https://example.com/favicon.ico"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="hero" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Image className="h-5 w-5 mr-2" />
                Hero Section
              </CardTitle>
              <CardDescription>
                Customize the main banner section of your homepage
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="hero_title">Hero Title</Label>
                <Input
                  id="hero_title"
                  value={layoutSettings.hero_title}
                  onChange={(e) => handleChange('hero_title', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="hero_subtitle">Hero Subtitle</Label>
                <Textarea
                  id="hero_subtitle"
                  value={layoutSettings.hero_subtitle}
                  onChange={(e) => handleChange('hero_subtitle', e.target.value)}
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="hero_cta_primary">Primary Button Text</Label>
                  <Input
                    id="hero_cta_primary"
                    value={layoutSettings.hero_cta_primary}
                    onChange={(e) => handleChange('hero_cta_primary', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="hero_cta_secondary">Secondary Button Text</Label>
                  <Input
                    id="hero_cta_secondary"
                    value={layoutSettings.hero_cta_secondary}
                    onChange={(e) => handleChange('hero_cta_secondary', e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="colors" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Palette className="h-5 w-5 mr-2" />
                Colors & Typography
              </CardTitle>
              <CardDescription>
                Customize the visual appearance of your website
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="primary_color">Primary Color</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="primary_color"
                      type="color"
                      value={layoutSettings.primary_color}
                      onChange={(e) => handleChange('primary_color', e.target.value)}
                      className="w-16 h-10"
                    />
                    <Input
                      value={layoutSettings.primary_color}
                      onChange={(e) => handleChange('primary_color', e.target.value)}
                      className="flex-1"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="secondary_color">Secondary Color</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="secondary_color"
                      type="color"
                      value={layoutSettings.secondary_color}
                      onChange={(e) => handleChange('secondary_color', e.target.value)}
                      className="w-16 h-10"
                    />
                    <Input
                      value={layoutSettings.secondary_color}
                      onChange={(e) => handleChange('secondary_color', e.target.value)}
                      className="flex-1"
                    />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="accent_color">Accent Color</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="accent_color"
                      type="color"
                      value={layoutSettings.accent_color}
                      onChange={(e) => handleChange('accent_color', e.target.value)}
                      className="w-16 h-10"
                    />
                    <Input
                      value={layoutSettings.accent_color}
                      onChange={(e) => handleChange('accent_color', e.target.value)}
                      className="flex-1"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="background_color">Background Color</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="background_color"
                      type="color"
                      value={layoutSettings.background_color}
                      onChange={(e) => handleChange('background_color', e.target.value)}
                      className="w-16 h-10"
                    />
                    <Input
                      value={layoutSettings.background_color}
                      onChange={(e) => handleChange('background_color', e.target.value)}
                      className="flex-1"
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="font_family">Font Family</Label>
                <Select
                  value={layoutSettings.font_family}
                  onValueChange={(value) => handleChange('font_family', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Inter">Inter</SelectItem>
                    <SelectItem value="Roboto">Roboto</SelectItem>
                    <SelectItem value="Open Sans">Open Sans</SelectItem>
                    <SelectItem value="Lato">Lato</SelectItem>
                    <SelectItem value="Montserrat">Montserrat</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="layout" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Layout className="h-5 w-5 mr-2" />
                Layout Options
              </CardTitle>
              <CardDescription>
                Configure the layout structure of your website
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="header_layout">Header Layout</Label>
                  <Select
                    value={layoutSettings.header_layout}
                    onValueChange={(value) => handleChange('header_layout', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="default">Default</SelectItem>
                      <SelectItem value="centered">Centered</SelectItem>
                      <SelectItem value="minimal">Minimal</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="footer_layout">Footer Layout</Label>
                  <Select
                    value={layoutSettings.footer_layout}
                    onValueChange={(value) => handleChange('footer_layout', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="default">Default</SelectItem>
                      <SelectItem value="minimal">Minimal</SelectItem>
                      <SelectItem value="extended">Extended</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="contact" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Contact Information</CardTitle>
              <CardDescription>
                Update your business contact details and social media links
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="contact_email">Contact Email</Label>
                  <Input
                    id="contact_email"
                    type="email"
                    value={layoutSettings.contact_email}
                    onChange={(e) => handleChange('contact_email', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="contact_phone">Contact Phone</Label>
                  <Input
                    id="contact_phone"
                    type="tel"
                    value={layoutSettings.contact_phone}
                    onChange={(e) => handleChange('contact_phone', e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="contact_address">Address</Label>
                <Textarea
                  id="contact_address"
                  value={layoutSettings.contact_address}
                  onChange={(e) => handleChange('contact_address', e.target.value)}
                  rows={2}
                />
              </div>

              <div className="space-y-4">
                <h3 className="font-semibold">Social Media Links</h3>
                <div className="grid grid-cols-1 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="social_facebook">Facebook URL</Label>
                    <Input
                      id="social_facebook"
                      type="url"
                      value={layoutSettings.social_facebook}
                      onChange={(e) => handleChange('social_facebook', e.target.value)}
                      placeholder="https://facebook.com/yourpage"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="social_twitter">Twitter URL</Label>
                    <Input
                      id="social_twitter"
                      type="url"
                      value={layoutSettings.social_twitter}
                      onChange={(e) => handleChange('social_twitter', e.target.value)}
                      placeholder="https://twitter.com/yourhandle"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="social_instagram">Instagram URL</Label>
                    <Input
                      id="social_instagram"
                      type="url"
                      value={layoutSettings.social_instagram}
                      onChange={(e) => handleChange('social_instagram', e.target.value)}
                      placeholder="https://instagram.com/yourhandle"
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

