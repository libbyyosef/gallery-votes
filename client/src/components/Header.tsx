import React from 'react'
import { Box, Button, HStack, Heading, Icon } from '@chakra-ui/react'
import { FiDownload } from 'react-icons/fi'


interface HeaderProps { onExport: () => void }


export const Header: React.FC<HeaderProps> = ({ onExport }) => (
<Box as="header" position="sticky" top={0} zIndex={10} bg="app.surface" boxShadow="elev" px={4} py={3}>
<HStack justify="space-between">
<Heading as="h1" size="md" color="app.text" m={0}>Gallery Votes - Libby Yosef</Heading>
<Button onClick={onExport} leftIcon={<Icon as={FiDownload} />} bg="app.accent" color="#0b1020" _hover={{ filter: 'brightness(1.05)' }}>
Export CSV
</Button>
</HStack>
</Box>
)